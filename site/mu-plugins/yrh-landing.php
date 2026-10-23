<?php
/**
 * Plugin Name: YRH destination guides (EN / FR / AR)
 * Description: Multilingual destination landing pages at /en|fr|ar/esim-<destination>/ with live plans and prices, hreflang, schema and sitemap.
 * Content lives in wp-content/mu-plugins/yrh-landing/{en,fr,ar}.json.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const YRH_LP_VER = 3;

/* destination key => product slug and URL slugs per language */
function yrh_lp_map() {
	return array(
		'algeria' => array( 'product' => 'algeria-esim', 'en' => 'algeria', 'fr' => 'algerie', 'ar' => 'algeria' ),
		'morocco' => array( 'product' => 'morocco-esim', 'en' => 'morocco', 'fr' => 'maroc', 'ar' => 'morocco' ),
		'tunisia' => array( 'product' => 'tunisia-esim', 'en' => 'tunisia', 'fr' => 'tunisie', 'ar' => 'tunisia' ),
		'turkey'  => array( 'product' => 'turkey-esim', 'en' => 'turkey', 'fr' => 'turquie', 'ar' => 'turkey' ),
		'saudi'   => array( 'product' => 'saudi-arabia-esim', 'en' => 'saudi-arabia', 'fr' => 'arabie-saoudite', 'ar' => 'saudi-arabia' ),
		'egypt'   => array( 'product' => 'egypt-esim', 'en' => 'egypt', 'fr' => 'egypte', 'ar' => 'egypt' ),
	);
}

function yrh_lp_langs() {
	return array( 'en', 'fr', 'ar' );
}

function yrh_lp_ui( $lang ) {
	$ui = array(
		'en' => array( 'plans' => 'Popular plans', 'data' => 'Data', 'valid' => 'Validity', 'price' => 'Price', 'buy' => 'Choose', 'all' => 'See all plans', 'days' => '%d days', 'day' => '%d day', 'faq' => 'Frequently asked questions', 'help' => 'Questions before you buy? A real person answers on WhatsApp in English, French or Arabic:', 'more' => 'Other destination guides', 'refund' => 'Works or your money back', 'locale' => 'en_US', 'html' => 'en' ),
		'fr' => array( 'plans' => 'Forfaits populaires', 'data' => 'Données', 'valid' => 'Validité', 'price' => 'Prix', 'buy' => 'Choisir', 'all' => 'Voir tous les forfaits', 'days' => '%d jours', 'day' => '%d jour', 'faq' => 'Questions fréquentes', 'help' => 'Une question avant d’acheter ? Une vraie personne vous répond sur WhatsApp en français, arabe ou anglais :', 'more' => 'Autres guides', 'refund' => 'Ça marche ou on vous rembourse', 'locale' => 'fr_FR', 'html' => 'fr' ),
		'ar' => array( 'plans' => 'الباقات الأكثر طلباً', 'data' => 'البيانات', 'valid' => 'المدة', 'price' => 'السعر', 'buy' => 'اختر', 'all' => 'كل الباقات', 'days' => '%d يوم', 'day' => '%d يوم', 'faq' => 'أسئلة شائعة', 'help' => 'عندك سؤال قبل الشراء؟ يرد عليك شخص حقيقي على واتساب بالعربية أو الفرنسية أو الإنجليزية:', 'more' => 'أدلة وجهات أخرى', 'refund' => 'تعمل أو نرجع لك مالك', 'locale' => 'ar_AR', 'html' => 'ar' ),
	);
	return $ui[ $lang ];
}

function yrh_lp_money( $amount, $lang ) {
	if ( 'fr' === $lang ) {
		return number_format( (float) $amount, 2, ',', ' ' ) . ' $';
	}
	return '$' . number_format( (float) $amount, 2 );
}

function yrh_lp_content( $lang ) {
	static $mem = array();
	if ( isset( $mem[ $lang ] ) ) {
		return $mem[ $lang ];
	}
	$file = __DIR__ . '/yrh-landing/' . $lang . '.json';
	$data = is_readable( $file ) ? json_decode( (string) file_get_contents( $file ), true ) : null;
	return ( $mem[ $lang ] = ( is_array( $data ) && isset( $data['pages'] ) ) ? $data['pages'] : array() );
}

function yrh_lp_url( $key, $lang ) {
	$m = yrh_lp_map();
	return home_url( '/' . $lang . '/esim-' . $m[ $key ][ $lang ] . '/' );
}

/* page exists only when its copy exists */
function yrh_lp_has( $key, $lang ) {
	$c = yrh_lp_content( $lang );
	return ! empty( $c[ $key ]['h1'] );
}

/* ---------- routing ---------- */
add_action(
	'init',
	function () {
		add_rewrite_rule( '^(en|fr|ar)/esim-([a-z-]+)/?$', 'index.php?yrh_lp_lang=$matches[1]&yrh_lp_slug=$matches[2]', 'top' );
		if ( (int) get_option( 'yrh_lp_ver' ) !== YRH_LP_VER ) {
			update_option( 'yrh_lp_ver', YRH_LP_VER, false );
			flush_rewrite_rules( false );
		}
	}
);
add_filter(
	'query_vars',
	function ( $v ) {
		$v[] = 'yrh_lp_lang';
		$v[] = 'yrh_lp_slug';
		return $v;
	}
);

/* array( key, lang ) for the current request, or null */
function yrh_lp_current() {
	static $cur = false;
	if ( false !== $cur ) {
		return $cur;
	}
	$lang = get_query_var( 'yrh_lp_lang' );
	$slug = get_query_var( 'yrh_lp_slug' );
	$cur  = null;
	if ( $lang && $slug && in_array( $lang, yrh_lp_langs(), true ) ) {
		foreach ( yrh_lp_map() as $key => $m ) {
			if ( $m[ $lang ] === $slug && yrh_lp_has( $key, $lang ) ) {
				$cur = array( $key, $lang );
				break;
			}
		}
	}
	return $cur;
}

function yrh_lp_product( $key ) {
	$m  = yrh_lp_map();
	$pp = get_page_by_path( $m[ $key ]['product'], OBJECT, 'product' );
	if ( ! $pp || ! function_exists( 'yrh_product' ) ) {
		return null;
	}
	return yrh_product( $pp->ID );
}

function yrh_lp_fill( $text, $from ) {
	return str_replace( '{FROM}', $from, (string) $text );
}

/* a short plan table: per data size, the longest validity (then the cheapest); at most 6 rows */
function yrh_lp_pick_plans( $d ) {
	$by = array();
	foreach ( $d['plans'] as $v ) {
		if ( ! $v['avail'] || $v['gb'] <= 0 || $v['qual'] ) {
			continue;
		}
		$k = (string) $v['gb'];
		if ( ! isset( $by[ $k ] ) || $v['days'] > $by[ $k ]['days'] || ( $v['days'] === $by[ $k ]['days'] && $v['cents'] < $by[ $k ]['cents'] ) ) {
			$by[ $k ] = $v;
		}
	}
	uasort(
		$by,
		function ( $a, $b ) {
			return $a['gb'] < $b['gb'] ? -1 : 1;
		}
	);
	$rows = array_values( $by );
	if ( count( $rows ) > 6 ) {
		$want = array( 1, 3, 5, 10, 20, 50 );
		$keep = array();
		foreach ( $want as $w ) {
			foreach ( $rows as $r ) {
				if ( abs( $r['gb'] - $w ) < 0.01 ) {
					$keep[] = $r;
				}
			}
		}
		$rows = count( $keep ) >= 3 ? $keep : array_slice( $rows, 0, 6 );
	}
	return $rows;
}

/* ---------- head: title, description, hreflang, canonical, social, schema ---------- */
add_filter(
	'pre_get_document_title',
	function ( $t ) {
		$cur = yrh_lp_current();
		if ( ! $cur ) {
			return $t;
		}
		list( $key, $lang ) = $cur;
		$c   = yrh_lp_content( $lang );
		$d   = yrh_lp_product( $key );
		$from = $d ? yrh_lp_money( $d['min'], $lang ) : '';
		return yrh_lp_fill( $c[ $key ]['title'], $from ) . ' | YRH eSIM';
	},
	99
);

add_filter(
	'language_attributes',
	function ( $out ) {
		$cur = yrh_lp_current();
		if ( ! $cur ) {
			return $out;
		}
		return 'lang="' . esc_attr( yrh_lp_ui( $cur[1] )['html'] ) . '"';
	}
);

add_filter(
	'wp_robots',
	function ( $r ) {
		if ( yrh_lp_current() ) {
			unset( $r['noindex'], $r['nofollow'] );
			$r['index']             = true;
			$r['follow']            = true;
			$r['max-image-preview'] = 'large';
		}
		return $r;
	},
	99
);

add_action(
	'wp_head',
	function () {
		$cur = yrh_lp_current();
		if ( ! $cur ) {
			return;
		}
		list( $key, $lang ) = $cur;
		$c    = yrh_lp_content( $lang );
		$p    = $c[ $key ];
		$d    = yrh_lp_product( $key );
		$from = $d ? yrh_lp_money( $d['min'], $lang ) : '';
		$url  = yrh_lp_url( $key, $lang );
		$desc = yrh_lp_fill( $p['meta'], $from );
		$img  = ( $d && $d['img_l'] ) ? $d['img_l'] : 'https://yrh.ai/wp-content/uploads/yrh-ads/us-roaming-1.png';
		$ttl  = wp_get_document_title();

		printf( "<meta name=\"description\" content=\"%s\">\n", esc_attr( $desc ) );
		printf( "<link rel=\"canonical\" href=\"%s\">\n", esc_url( $url ) );
		foreach ( yrh_lp_langs() as $l ) {
			if ( yrh_lp_has( $key, $l ) ) {
				printf( "<link rel=\"alternate\" hreflang=\"%s\" href=\"%s\">\n", esc_attr( $l ), esc_url( yrh_lp_url( $key, $l ) ) );
			}
		}
		if ( yrh_lp_has( $key, 'en' ) ) {
			printf( "<link rel=\"alternate\" hreflang=\"x-default\" href=\"%s\">\n", esc_url( yrh_lp_url( $key, 'en' ) ) );
		}
		$og = array(
			'og:site_name'   => 'YRH eSIM',
			'og:locale'      => yrh_lp_ui( $lang )['locale'],
			'og:type'        => 'article',
			'og:title'       => $ttl,
			'og:description' => $desc,
			'og:url'         => $url,
			'og:image'       => $img,
		);
		foreach ( $og as $k => $v ) {
			printf( "<meta property=\"%s\" content=\"%s\">\n", esc_attr( $k ), esc_attr( $v ) );
		}
		printf( "<meta name=\"twitter:card\" content=\"summary_large_image\">\n<meta name=\"twitter:title\" content=\"%s\">\n<meta name=\"twitter:description\" content=\"%s\">\n<meta name=\"twitter:image\" content=\"%s\">\n", esc_attr( $ttl ), esc_attr( $desc ), esc_url( $img ) );

		$graph = array();
		if ( ! empty( $p['faq'] ) ) {
			$graph[] = array(
				'@type'      => 'FAQPage',
				'inLanguage' => $lang,
				'mainEntity' => array_map(
					function ( $f ) use ( $from ) {
						return array(
							'@type'          => 'Question',
							'name'           => yrh_lp_fill( $f['q'], $from ),
							'acceptedAnswer' => array( '@type' => 'Answer', 'text' => yrh_lp_fill( $f['a'], $from ) ),
						);
					},
					$p['faq']
				),
			);
		}
		$graph[] = array(
			'@type'           => 'BreadcrumbList',
			'itemListElement' => array(
				array( '@type' => 'ListItem', 'position' => 1, 'name' => 'YRH eSIM', 'item' => home_url( '/' ) ),
				array( '@type' => 'ListItem', 'position' => 2, 'name' => wp_strip_all_tags( $p['h1'] ), 'item' => $url ),
			),
		);
		echo '<script type="application/ld+json">' . wp_json_encode( array( '@context' => 'https://schema.org', '@graph' => $graph ), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . "</script>\n";
		?>
<style>
.yrh-lp{max-width:760px}
.yrh-lp-langs{display:flex;gap:.5rem;flex-wrap:wrap;margin:0 0 1rem;font-size:.9rem}
.yrh-lp-langs a,.yrh-lp-langs span{padding:.25rem .7rem;border-radius:999px;border:1px solid rgba(0,0,0,.15);text-decoration:none;color:inherit}
.yrh-lp-langs span{background:#0b121d;color:#fff;border-color:#0b121d}
.yrh-lp-plans{width:100%;border-collapse:collapse;margin:1rem 0 .5rem;font-size:1rem}
.yrh-lp-plans th,.yrh-lp-plans td{padding:.7rem .5rem;border-bottom:1px solid rgba(0,0,0,.1);text-align:start}
.yrh-lp-plans th{font-size:.8rem;text-transform:uppercase;letter-spacing:.04em;opacity:.7}
.yrh-lp-plans td.p{font-weight:600;white-space:nowrap}
.yrh-lp-btn{display:inline-block;padding:.55rem 1rem;border-radius:8px;background:#0b121d;color:#fff!important;text-decoration:none;font-weight:600;white-space:nowrap}
.yrh-lp-cta{display:inline-block;margin:.5rem 0 1.5rem;padding:.85rem 1.4rem;border-radius:10px;background:#f5b400;color:#0b121d!important;font-weight:700;text-decoration:none}
.yrh-lp-faq details{border-bottom:1px solid rgba(0,0,0,.1);padding:.8rem 0}
.yrh-lp-faq summary{cursor:pointer;font-weight:600}
.yrh-lp-faq details p{margin:.5rem 0 0}
.yrh-lp-help{background:rgba(0,0,0,.04);border-radius:10px;padding:1rem 1.2rem;margin:1.5rem 0}
.yrh-lp-more{display:flex;flex-wrap:wrap;gap:.5rem;padding:0;list-style:none}
.yrh-lp-more a{display:inline-block;padding:.35rem .8rem;border:1px solid rgba(0,0,0,.15);border-radius:999px;text-decoration:none;color:inherit}
.yrh-lp[dir=rtl]{text-align:right}
.yrh-lp[dir=rtl] .yrh-lp-plans td.p,.yrh-lp[dir=rtl] .ltr{direction:ltr;unicode-bidi:isolate}
@media (max-width:560px){.yrh-lp-plans th:nth-child(3),.yrh-lp-plans td:nth-child(3){display:none}}
</style>
		<?php
	},
	2
);

/* ---------- render ---------- */
add_action(
	'template_redirect',
	function () {
		$cur = yrh_lp_current();
		if ( ! $cur ) {
			if ( get_query_var( 'yrh_lp_lang' ) ) {
				global $wp_query;
				$wp_query->set_404();
				status_header( 404 );
			}
			return;
		}
		list( $key, $lang ) = $cur;
		$c    = yrh_lp_content( $lang );
		$p    = $c[ $key ];
		$ui   = yrh_lp_ui( $lang );
		$d    = yrh_lp_product( $key );
		$from = $d ? yrh_lp_money( $d['min'], $lang ) : '';
		$dir  = 'ar' === $lang ? 'rtl' : 'ltr';
		$wa   = 'https://wa.me/34642377474';

		global $wp_query;
		$wp_query->is_404  = false;
		$wp_query->is_home = false;
		status_header( 200 );

		get_header();
		?>
<section class="y7-sec y7-sec--tight y7-sec--paper">
	<div class="y7-wrap">
		<div class="y7-page yrh-lp" dir="<?php echo esc_attr( $dir ); ?>" lang="<?php echo esc_attr( $lang ); ?>">
			<nav class="yrh-lp-langs" aria-label="Language">
				<?php
				$names = array( 'en' => 'English', 'fr' => 'Français', 'ar' => 'العربية' );
				foreach ( yrh_lp_langs() as $l ) {
					if ( ! yrh_lp_has( $key, $l ) ) {
						continue;
					}
					if ( $l === $lang ) {
						echo '<span>' . esc_html( $names[ $l ] ) . '</span>';
					} else {
						echo '<a href="' . esc_url( yrh_lp_url( $key, $l ) ) . '" hreflang="' . esc_attr( $l ) . '" lang="' . esc_attr( $l ) . '">' . esc_html( $names[ $l ] ) . '</a>';
					}
				}
				?>
			</nav>
			<h1 class="y7-h2 y7-pagetitle"><?php echo esc_html( yrh_lp_fill( $p['h1'], $from ) ); ?></h1>
			<div class="y7-prose">
				<?php echo wp_kses_post( yrh_lp_fill( $p['intro'], $from ) ); ?>

				<?php if ( $d ) : ?>
					<h2><?php echo esc_html( $ui['plans'] ); ?></h2>
					<table class="yrh-lp-plans">
						<thead><tr><th><?php echo esc_html( $ui['data'] ); ?></th><th><?php echo esc_html( $ui['valid'] ); ?></th><th><?php echo esc_html( $ui['price'] ); ?></th><th></th></tr></thead>
						<tbody>
						<?php foreach ( yrh_lp_pick_plans( $d ) as $v ) : ?>
							<tr>
								<td class="ltr"><?php echo esc_html( $v['label'] ); ?></td>
								<td><?php echo esc_html( sprintf( 1 === (int) $v['days'] ? $ui['day'] : $ui['days'], (int) $v['days'] ) ); ?></td>
								<td class="p"><?php echo esc_html( yrh_lp_money( $v['price'], $lang ) ); ?></td>
								<td><a class="yrh-lp-btn" href="<?php echo esc_url( add_query_arg( 'variant', $v['id'], $d['url'] ) ); ?>"><?php echo esc_html( $ui['buy'] ); ?></a></td>
							</tr>
						<?php endforeach; ?>
						</tbody>
					</table>
					<a class="yrh-lp-cta" href="<?php echo esc_url( $d['url'] ); ?>"><?php echo esc_html( ! empty( $p['cta'] ) ? $p['cta'] : $ui['all'] ); ?></a>
				<?php endif; ?>

				<?php foreach ( (array) $p['sections'] as $s ) : ?>
					<h2><?php echo esc_html( yrh_lp_fill( $s['h2'], $from ) ); ?></h2>
					<?php echo wp_kses_post( yrh_lp_fill( $s['html'], $from ) ); ?>
				<?php endforeach; ?>

				<p class="yrh-lp-help"><?php echo esc_html( $ui['help'] ); ?> <a href="<?php echo esc_url( $wa ); ?>" dir="ltr">+34 642 377 474</a>. <strong><?php echo esc_html( $ui['refund'] ); ?></strong>.</p>

				<?php if ( ! empty( $p['faq'] ) ) : ?>
					<h2><?php echo esc_html( $ui['faq'] ); ?></h2>
					<div class="yrh-lp-faq">
						<?php foreach ( $p['faq'] as $f ) : ?>
							<details><summary><?php echo esc_html( yrh_lp_fill( $f['q'], $from ) ); ?></summary><p><?php echo esc_html( yrh_lp_fill( $f['a'], $from ) ); ?></p></details>
						<?php endforeach; ?>
					</div>
				<?php endif; ?>

				<?php if ( $d ) : ?>
					<a class="yrh-lp-cta" href="<?php echo esc_url( $d['url'] ); ?>"><?php echo esc_html( ! empty( $p['cta'] ) ? $p['cta'] : $ui['all'] ); ?></a>
				<?php endif; ?>

				<h2><?php echo esc_html( $ui['more'] ); ?></h2>
				<ul class="yrh-lp-more">
					<?php
					foreach ( array_keys( yrh_lp_map() ) as $k ) {
						if ( $k === $key || ! yrh_lp_has( $k, $lang ) ) {
							continue;
						}
						echo '<li><a href="' . esc_url( yrh_lp_url( $k, $lang ) ) . '">' . esc_html( wp_strip_all_tags( $c[ $k ]['h1'] ) ) . '</a></li>';
					}
					?>
				</ul>
			</div>
		</div>
	</div>
</section>
		<?php
		get_footer();
		exit;
	},
	1
);

/* ---------- sitemap ---------- */
add_action(
	'wp_sitemaps_init',
	function ( $sitemaps ) {
		if ( ! class_exists( 'WP_Sitemaps_Provider' ) ) {
			return;
		}
		$sitemaps->registry->add_provider( 'yrhguides', new YRH_LP_Sitemap() );
	}
);

if ( class_exists( 'WP_Sitemaps_Provider' ) || ( defined( 'ABSPATH' ) && file_exists( ABSPATH . WPINC . '/sitemaps/class-wp-sitemaps-provider.php' ) ) ) {
	if ( ! class_exists( 'WP_Sitemaps_Provider' ) ) {
		require_once ABSPATH . WPINC . '/sitemaps/class-wp-sitemaps-provider.php';
	}
	class YRH_LP_Sitemap extends WP_Sitemaps_Provider {
		public function __construct() {
			$this->name        = 'yrhguides';
			$this->object_type = 'yrhguides';
		}
		public function get_url_list( $page_num, $object_subtype = '' ) {
			$out = array();
			foreach ( array_keys( yrh_lp_map() ) as $k ) {
				foreach ( yrh_lp_langs() as $l ) {
					if ( yrh_lp_has( $k, $l ) ) {
						$out[] = array( 'loc' => yrh_lp_url( $k, $l ) );
					}
				}
			}
			return $out;
		}
		public function get_max_num_pages( $object_subtype = '' ) {
			return 1;
		}
	}
}
