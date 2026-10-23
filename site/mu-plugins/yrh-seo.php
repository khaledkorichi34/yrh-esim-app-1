<?php
/**
 * Plugin Name: YRH SEO
 * Description: Titles, meta descriptions, social previews (Open Graph), structured data and a clean sitemap for yrh.ai.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

const YRH_SEO_DEFAULT_IMG = 'https://yrh.ai/wp-content/uploads/yrh-ads/us-roaming-1.png';

function yrh_seo_clip( $text, $max = 158 ) {
	$text = trim( preg_replace( '/\s+/u', ' ', wp_strip_all_tags( html_entity_decode( (string) $text, ENT_QUOTES, 'UTF-8' ) ) ) );
	if ( mb_strlen( $text ) <= $max ) {
		return $text;
	}
	$cut = mb_substr( $text, 0, $max - 1 );
	$sp  = mb_strrpos( $cut, ' ' );
	return rtrim( mb_substr( $cut, 0, $sp ? $sp : $max - 1 ), ' ,.;:' ) . '…';
}

/* Destination name without the trailing "eSIM": "Morocco eSIM" -> "Morocco". */
function yrh_seo_dest( $product ) {
	$name = html_entity_decode( $product->get_name(), ENT_QUOTES, 'UTF-8' );
	return trim( preg_replace( '/\s*e-?SIM\s*$/i', '', $name ) );
}

function yrh_seo_price_range( $product ) {
	$min = $max = 0;
	if ( $product->is_type( 'variable' ) ) {
		$min = (float) $product->get_variation_price( 'min' );
		$max = (float) $product->get_variation_price( 'max' );
	} else {
		$min = $max = (float) $product->get_price();
	}
	return array( $min, $max );
}

function yrh_seo_money( $n ) {
	return '$' . number_format( (float) $n, 2 );
}

function yrh_seo_current_product() {
	if ( ! function_exists( 'is_product' ) || ! is_product() ) {
		return null;
	}
	$p = wc_get_product( get_queried_object_id() );
	return $p ? $p : null;
}

/* ---------- titles ---------- */
add_filter(
	'document_title_parts',
	function ( $parts ) {
		$p = yrh_seo_current_product();
		if ( $p ) {
			list( $min ) = yrh_seo_price_range( $p );
			$dest        = yrh_seo_dest( $p );
			$parts['title'] = $min > 0
				? sprintf( '%s eSIM – Prepaid Travel Data from %s', $dest, yrh_seo_money( $min ) )
				: sprintf( '%s eSIM – Prepaid Travel Data', $dest );
			return $parts;
		}
		if ( is_front_page() ) {
			$parts['title']   = 'Travel eSIM for 240+ Destinations – Prepaid Data, No Roaming';
			$parts['tagline'] = '';
			unset( $parts['tagline'] );
		} elseif ( function_exists( 'is_shop' ) && is_shop() ) {
			$parts['title'] = 'All eSIM Destinations & Prices';
		}
		return $parts;
	},
	20
);

/* ---------- description ---------- */
function yrh_seo_description() {
	$p = yrh_seo_current_product();
	if ( $p ) {
		list( $min ) = yrh_seo_price_range( $p );
		$dest        = yrh_seo_dest( $p );
		$from        = $min > 0 ? ' from ' . yrh_seo_money( $min ) : '';
		return yrh_seo_clip( sprintf( '%s eSIM%s: prepaid mobile data for your trip, delivered by email in minutes. Keep your number for WhatsApp, hotspot included, real human support.', $dest, $from ) );
	}
	if ( is_front_page() ) {
		return 'Prepaid travel eSIM data for 240+ destinations. Install before you fly, keep your WhatsApp number, hotspot included. QR by email in minutes, human support.';
	}
	if ( function_exists( 'is_shop' ) && is_shop() ) {
		return 'Compare prepaid eSIM data plans for 240+ countries and regions: data, validity and price per GB. Delivered by email in minutes, hotspot included.';
	}
	if ( function_exists( 'is_product_category' ) && is_product_category() ) {
		$t = get_queried_object();
		return yrh_seo_clip( sprintf( 'Prepaid eSIM data plans for %s. Compare data, validity and price, get your QR code by email in minutes.', $t ? $t->name : 'travel' ) );
	}
	if ( is_singular() ) {
		$post = get_queried_object();
		if ( $post && ! empty( $post->post_content ) ) {
			$txt = has_excerpt( $post ) ? $post->post_excerpt : strip_shortcodes( $post->post_content );
			return yrh_seo_clip( $txt );
		}
	}
	return 'Prepaid travel eSIM data for 240+ destinations, delivered by email in minutes.';
}

function yrh_seo_image() {
	$p = yrh_seo_current_product();
	if ( $p && $p->get_image_id() ) {
		$src = wp_get_attachment_image_url( $p->get_image_id(), 'large' );
		if ( $src ) {
			return $src;
		}
	}
	return YRH_SEO_DEFAULT_IMG;
}

function yrh_seo_url() {
	if ( is_front_page() ) {
		return home_url( '/' );
	}
	if ( is_singular() ) {
		return get_permalink( get_queried_object_id() );
	}
	if ( function_exists( 'is_shop' ) && is_shop() ) {
		return wc_get_page_permalink( 'shop' );
	}
	if ( is_tax() || is_category() ) {
		$l = get_term_link( get_queried_object() );
		return is_wp_error( $l ) ? home_url( '/' ) : $l;
	}
	return home_url( add_query_arg( array() ) );
}

add_action(
	'wp_head',
	function () {
		if ( is_404() || is_search() || ( function_exists( 'yrh_lp_current' ) && yrh_lp_current() ) ) {
			return;
		}
		$desc  = yrh_seo_description();
		$title = wp_get_document_title();
		$url   = yrh_seo_url();
		$img   = yrh_seo_image();
		$p     = yrh_seo_current_product();

		/* the theme prints its own description on the front page; skip ours there */
		if ( ! is_front_page() ) {
			printf( "<meta name=\"description\" content=\"%s\">\n", esc_attr( $desc ) );
		}
		$og = array(
			'og:site_name'   => 'YRH eSIM',
			'og:locale'      => 'en_US',
			'og:type'        => $p ? 'product' : 'website',
			'og:title'       => $title,
			'og:description' => is_front_page() ? $desc : $desc,
			'og:url'         => $url,
			'og:image'       => $img,
		);
		foreach ( $og as $k => $v ) {
			printf( "<meta property=\"%s\" content=\"%s\">\n", esc_attr( $k ), esc_attr( $v ) );
		}
		if ( $p ) {
			list( $min ) = yrh_seo_price_range( $p );
			if ( $min > 0 ) {
				printf( "<meta property=\"product:price:amount\" content=\"%s\">\n<meta property=\"product:price:currency\" content=\"USD\">\n", esc_attr( number_format( $min, 2, '.', '' ) ) );
			}
		}
		echo "<meta name=\"twitter:card\" content=\"summary_large_image\">\n";
		printf( "<meta name=\"twitter:title\" content=\"%s\">\n<meta name=\"twitter:description\" content=\"%s\">\n<meta name=\"twitter:image\" content=\"%s\">\n", esc_attr( $title ), esc_attr( $desc ), esc_url( $img ) );

		/* structured data */
		$graph = array();
		if ( is_front_page() ) {
			$graph[] = array(
				'@type'        => 'Organization',
				'@id'          => home_url( '/#org' ),
				'name'         => 'YRH eSIM',
				'url'          => home_url( '/' ),
				'logo'         => YRH_SEO_DEFAULT_IMG,
				'email'        => 'yrhesim@gmail.com',
				'contactPoint' => array(
					'@type'             => 'ContactPoint',
					'contactType'       => 'customer support',
					'telephone'         => '+34642377474',
					'availableLanguage' => array( 'English', 'French', 'Arabic' ),
				),
			);
			$graph[] = array(
				'@type'           => 'WebSite',
				'@id'             => home_url( '/#website' ),
				'name'            => 'YRH eSIM',
				'url'             => home_url( '/' ),
				'publisher'       => array( '@id' => home_url( '/#org' ) ),
				'potentialAction' => array(
					'@type'       => 'SearchAction',
					'target'      => home_url( '/?s={search_term_string}&post_type=product' ),
					'query-input' => 'required name=search_term_string',
				),
			);
		}
		if ( $p ) {
			list( $min, $max ) = yrh_seo_price_range( $p );
			$count             = $p->is_type( 'variable' ) ? count( $p->get_children() ) : 1;
			$dest              = yrh_seo_dest( $p );
			$prod              = array(
				'@type'       => 'Product',
				'name'        => $dest . ' eSIM',
				'description' => $desc,
				'url'         => $url,
				'image'       => $img,
				'sku'         => $p->get_sku(),
				'category'    => 'Prepaid eSIM data plan',
				'brand'       => array( '@type' => 'Brand', 'name' => 'YRH eSIM' ),
			);
			if ( $min > 0 ) {
				$prod['offers'] = array(
					'@type'           => 'AggregateOffer',
					'priceCurrency'   => 'USD',
					'lowPrice'        => number_format( $min, 2, '.', '' ),
					'highPrice'       => number_format( $max, 2, '.', '' ),
					'offerCount'      => $count,
					'availability'    => 'https://schema.org/InStock',
					'url'             => $url,
					'seller'          => array( '@type' => 'Organization', 'name' => 'YRH eSIM' ),
				);
			}
			$graph[] = $prod;
			$graph[] = array(
				'@type'           => 'BreadcrumbList',
				'itemListElement' => array(
					array( '@type' => 'ListItem', 'position' => 1, 'name' => 'Home', 'item' => home_url( '/' ) ),
					array( '@type' => 'ListItem', 'position' => 2, 'name' => 'Destinations', 'item' => wc_get_page_permalink( 'shop' ) ),
					array( '@type' => 'ListItem', 'position' => 3, 'name' => $dest . ' eSIM', 'item' => $url ),
				),
			);
		}
		if ( $graph ) {
			echo '<script type="application/ld+json">' . wp_json_encode( array( '@context' => 'https://schema.org', '@graph' => $graph ), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE ) . "</script>\n";
		}
	},
	5
);

/* WooCommerce's own product markup would duplicate ours. */
add_filter( 'woocommerce_structured_data_product', '__return_empty_array' );

/* ---------- robots ---------- */
add_filter(
	'wp_robots',
	function ( $robots ) {
		if ( is_search() || is_tax( 'product_tag' ) || is_author() || is_date() || is_category() || ( is_home() && ! is_front_page() ) ) {
			$robots['noindex'] = true;
			$robots['follow']  = true;
			unset( $robots['max-image-preview'] );
		}
		return $robots;
	}
);

/* ---------- sitemap: only pages people should land on ---------- */
add_filter(
	'wp_sitemaps_add_provider',
	function ( $provider, $name ) {
		return 'users' === $name ? false : $provider;
	},
	10,
	2
);
add_filter(
	'wp_sitemaps_taxonomies',
	function ( $taxonomies ) {
		unset( $taxonomies['product_tag'], $taxonomies['category'], $taxonomies['post_tag'] );
		return $taxonomies;
	}
);
add_filter(
	'wp_sitemaps_post_types',
	function ( $types ) {
		unset( $types['post'] );
		return $types;
	}
);
add_filter(
	'wp_sitemaps_posts_query_args',
	function ( $args, $post_type ) {
		if ( 'page' === $post_type && function_exists( 'wc_get_page_id' ) ) {
			$skip = array_filter( array( wc_get_page_id( 'cart' ), wc_get_page_id( 'checkout' ), wc_get_page_id( 'myaccount' ) ), function ( $id ) { return $id > 0; } );
			$args['post__not_in'] = array_merge( isset( $args['post__not_in'] ) ? (array) $args['post__not_in'] : array(), $skip );
		}
		return $args;
	},
	10,
	2
);

/* Hide author archives (they reveal the admin login name). */
add_action(
	'template_redirect',
	function () {
		if ( is_author() ) {
			wp_safe_redirect( home_url( '/' ), 301 );
			exit;
		}
	}
);
