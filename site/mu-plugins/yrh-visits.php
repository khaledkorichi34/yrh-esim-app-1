<?php
/**
 * Plugin Name: YRH visits (country + source log)
 * Description: Counts real (JavaScript) visits with country and source, and serves a private daily report for the owner.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const YRH_VISITS_KEY = 'b7d42e9c51f08a3e6c27d915';
const YRH_VISITS_DB  = 2;

function yrh_visits_table() {
	global $wpdb;
	return $wpdb->prefix . 'yrh_visits';
}

/* Create or upgrade the table once. */
add_action(
	'init',
	function () {
		if ( (int) get_option( 'yrh_visits_db' ) === YRH_VISITS_DB ) {
			return;
		}
		global $wpdb;
		require_once ABSPATH . 'wp-admin/includes/upgrade.php';
		$t = yrh_visits_table();
		$c = $wpdb->get_charset_collate();
		dbDelta(
			"CREATE TABLE $t (
			id bigint(20) unsigned NOT NULL AUTO_INCREMENT,
			ts datetime NOT NULL,
			day date NOT NULL,
			vid char(16) NOT NULL,
			ip varchar(45) NULL,
			country char(2) NULL,
			path varchar(191) NOT NULL DEFAULT '',
			src varchar(64) NOT NULL DEFAULT '',
			PRIMARY KEY  (id),
			KEY day (day),
			KEY country (country)
			) $c;"
		);
		update_option( 'yrh_visits_db', YRH_VISITS_DB, false );
	}
);

/* Tiny beacon in the page footer: bots without JavaScript and logged-in admins are not counted. */
add_action(
	'wp_footer',
	function () {
		if ( is_admin() || current_user_can( 'manage_options' ) ) {
			return;
		}
		$url = esc_url_raw( rest_url( 'yrh/v1/hit' ) );
		?>
<script>
(function(){try{
if(navigator.webdriver)return;
var q=new URLSearchParams(location.search),d={p:location.pathname,s:q.get('utm_source')||'',r:document.referrer||''};
if(q.get('fbclid')&&!d.s)d.s='facebook';
if(q.get('gclid')&&!d.s)d.s='google-ads';
var b=JSON.stringify(d),u=<?php echo wp_json_encode( $url ); ?>;
if(navigator.sendBeacon){navigator.sendBeacon(u,new Blob([b],{type:'text/plain'}));}
else{fetch(u,{method:'POST',body:b,keepalive:true});}
}catch(e){}})();
</script>
		<?php
	},
	99
);

function yrh_visits_source( $s, $r ) {
	$s = strtolower( substr( preg_replace( '/[^A-Za-z0-9_.-]/', '', (string) $s ), 0, 40 ) );
	if ( $s ) {
		if ( in_array( $s, array( 'fb', 'ig', 'instagram', 'facebook', 'meta' ), true ) ) {
			return 'facebook';
		}
		return $s;
	}
	$host = strtolower( (string) wp_parse_url( (string) $r, PHP_URL_HOST ) );
	if ( '' === $host || false !== strpos( $host, 'yrh.ai' ) ) {
		return 'direct';
	}
	$map = array(
		'facebook' => 'facebook',
		'fb.'      => 'facebook',
		'instagram'=> 'instagram',
		'google'   => 'google',
		'bing'     => 'bing',
		'tiktok'   => 'tiktok',
		'linkedin' => 'linkedin',
		'lnkd'     => 'linkedin',
		'pinterest'=> 'pinterest',
		'youtube'  => 'youtube',
		't.co'     => 'x',
		'twitter'  => 'x',
		'whatsapp' => 'whatsapp',
		'telegram' => 'telegram',
		'chatgpt'  => 'chatgpt',
	);
	foreach ( $map as $needle => $name ) {
		if ( false !== strpos( $host, $needle ) ) {
			return $name;
		}
	}
	return substr( preg_replace( '/^www\./', '', $host ), 0, 60 );
}

function yrh_visits_ip() {
	$ip = isset( $_SERVER['REMOTE_ADDR'] ) ? (string) $_SERVER['REMOTE_ADDR'] : '';
	return filter_var( $ip, FILTER_VALIDATE_IP ) ? $ip : '';
}

function yrh_visits_server_country() {
	foreach ( array( 'HTTP_CF_IPCOUNTRY', 'GEOIP_COUNTRY_CODE', 'HTTP_X_COUNTRY_CODE', 'HTTP_X_GEO_COUNTRY' ) as $k ) {
		if ( ! empty( $_SERVER[ $k ] ) && preg_match( '/^[A-Z]{2}$/', strtoupper( $_SERVER[ $k ] ) ) ) {
			return strtoupper( $_SERVER[ $k ] );
		}
	}
	return null;
}

add_action(
	'rest_api_init',
	function () {
		register_rest_route(
			'yrh/v1',
			'/hit',
			array(
				'methods'             => 'POST',
				'permission_callback' => '__return_true',
				'callback'            => 'yrh_visits_hit',
			)
		);
		register_rest_route(
			'yrh/v1',
			'/visits-report',
			array(
				'methods'             => 'GET',
				'permission_callback' => function ( $req ) {
					return hash_equals( YRH_VISITS_KEY, (string) $req->get_param( 'k' ) );
				},
				'callback'            => 'yrh_visits_report',
			)
		);
	}
);

function yrh_visits_hit( WP_REST_Request $req ) {
	$ua = isset( $_SERVER['HTTP_USER_AGENT'] ) ? (string) $_SERVER['HTTP_USER_AGENT'] : '';
	if ( '' === $ua || preg_match( '/bot|crawl|spider|slurp|preview|headless|lighthouse|facebookexternalhit|python|curl|wget|httpclient|monitor/i', $ua ) ) {
		return new WP_REST_Response( null, 204 );
	}
	$ip = yrh_visits_ip();
	if ( '' === $ip ) {
		return new WP_REST_Response( null, 204 );
	}
	/* At most 60 hits per IP per hour. */
	$rk = 'yrh_v_' . md5( $ip );
	$n  = (int) get_transient( $rk );
	if ( $n >= 60 ) {
		return new WP_REST_Response( null, 204 );
	}
	set_transient( $rk, $n + 1, HOUR_IN_SECONDS );

	$d    = json_decode( (string) $req->get_body(), true );
	$d    = is_array( $d ) ? $d : array();
	$path = substr( preg_replace( '/[^\x20-\x7E]/', '', (string) ( $d['p'] ?? '/' ) ), 0, 190 );
	$src  = yrh_visits_source( $d['s'] ?? '', $d['r'] ?? '' );
	$day  = current_time( 'Y-m-d' );
	$vid  = substr( hash( 'sha256', $ip . '|' . $ua . '|' . $day . '|' . wp_salt( 'auth' ) ), 0, 16 );

	global $wpdb;
	$wpdb->insert(
		yrh_visits_table(),
		array(
			'ts'      => current_time( 'mysql' ),
			'day'     => $day,
			'vid'     => $vid,
			'ip'      => $ip,
			'country' => yrh_visits_server_country(),
			'path'    => $path ? $path : '/',
			'src'     => $src,
		)
	);
	return new WP_REST_Response( null, 204 );
}

/* Fill in countries for rows that have none (ip-api.com batch, 100 IPs per call), then forget IPs older than 2 days. */
function yrh_visits_resolve_countries() {
	global $wpdb;
	$t   = yrh_visits_table();
	$ips = $wpdb->get_col( "SELECT DISTINCT ip FROM $t WHERE country IS NULL AND ip IS NOT NULL LIMIT 500" );
	foreach ( array_chunk( $ips, 100 ) as $chunk ) {
		$res = wp_remote_post(
			'http://ip-api.com/batch?fields=status,countryCode,query',
			array(
				'timeout' => 15,
				'headers' => array( 'Content-Type' => 'application/json' ),
				'body'    => wp_json_encode( array_values( $chunk ) ),
			)
		);
		if ( is_wp_error( $res ) ) {
			break;
		}
		$rows = json_decode( wp_remote_retrieve_body( $res ), true );
		if ( ! is_array( $rows ) ) {
			break;
		}
		foreach ( $rows as $r ) {
			$cc = ( isset( $r['status'] ) && 'success' === $r['status'] && ! empty( $r['countryCode'] ) ) ? $r['countryCode'] : 'XX';
			$wpdb->update( $t, array( 'country' => $cc ), array( 'ip' => $r['query'] ?? '' ) );
		}
	}
	$wpdb->query( $wpdb->prepare( "UPDATE $t SET ip = NULL WHERE ip IS NOT NULL AND country IS NOT NULL AND day < %s", gmdate( 'Y-m-d', strtotime( current_time( 'Y-m-d' ) . ' -2 days' ) ) ) );
}

function yrh_visits_report( WP_REST_Request $req ) {
	global $wpdb;
	$t = yrh_visits_table();
	yrh_visits_resolve_countries();

	$day = (string) $req->get_param( 'day' );
	if ( ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $day ) ) {
		$day = gmdate( 'Y-m-d', strtotime( current_time( 'Y-m-d' ) . ' -1 day' ) );
	}
	$from7 = gmdate( 'Y-m-d', strtotime( $day . ' -6 days' ) );

	$out = array(
		'day'        => $day,
		'visitors'   => (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(DISTINCT vid) FROM $t WHERE day = %s", $day ) ),
		'pageviews'  => (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(*) FROM $t WHERE day = %s", $day ) ),
		'countries'  => $wpdb->get_results( $wpdb->prepare( "SELECT IFNULL(country,'??') AS country, COUNT(DISTINCT vid) AS visitors FROM $t WHERE day = %s GROUP BY country ORDER BY visitors DESC LIMIT 20", $day ), ARRAY_A ),
		'sources'    => $wpdb->get_results( $wpdb->prepare( "SELECT src AS source, COUNT(DISTINCT vid) AS visitors FROM $t WHERE day = %s GROUP BY src ORDER BY visitors DESC LIMIT 15", $day ), ARRAY_A ),
		'pages'      => $wpdb->get_results( $wpdb->prepare( "SELECT path, COUNT(*) AS views FROM $t WHERE day = %s GROUP BY path ORDER BY views DESC LIMIT 10", $day ), ARRAY_A ),
		'last7'      => $wpdb->get_results( $wpdb->prepare( "SELECT day, COUNT(DISTINCT vid) AS visitors, COUNT(*) AS pageviews FROM $t WHERE day BETWEEN %s AND %s GROUP BY day ORDER BY day", $from7, $day ), ARRAY_A ),
		'countries7' => $wpdb->get_results( $wpdb->prepare( "SELECT IFNULL(country,'??') AS country, COUNT(DISTINCT vid) AS visitors FROM $t WHERE day BETWEEN %s AND %s GROUP BY country ORDER BY visitors DESC LIMIT 15", $from7, $day ), ARRAY_A ),
		'checkout'   => (int) $wpdb->get_var( $wpdb->prepare( "SELECT COUNT(DISTINCT vid) FROM $t WHERE day = %s AND (path LIKE %s OR path LIKE %s)", $day, '/checkout%', '/cart%' ) ),
	);
	if ( function_exists( 'wc_get_orders' ) ) {
		$orders = wc_get_orders(
			array(
				'status'       => array( 'processing', 'completed' ),
				'date_created' => ( new DateTime( $day . ' 00:00:00', wp_timezone() ) )->getTimestamp() . '...' . ( new DateTime( $day . ' 23:59:59', wp_timezone() ) )->getTimestamp(),
				'limit'        => 100,
			)
		);
		$out['orders']  = count( $orders );
		$out['revenue'] = round( array_sum( array_map( function ( $o ) { return (float) $o->get_total(); }, $orders ) ), 2 );
	}
	return new WP_REST_Response( $out, 200, array( 'Cache-Control' => 'no-store' ) );
}
