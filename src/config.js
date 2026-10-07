// App settings. There are no secret keys in this app, on purpose.
//
// How an order flows:
//   1. The app reads the public catalog of your Shopify store.
//   2. "Buy" opens Shopify checkout with the chosen plan in the cart.
//   3. After payment, the Make automation orders the eSIM from eSIM Access
//      and emails the install link to the buyer.
//
// The eSIM Access Access Code stays in Make. Never put it in this app:
// anyone can unpack an Android app and read keys stored inside it.

export const SHOP_URL = 'https://07eqi1-zk.myshopify.com';

export const SUPPORT_EMAIL = 'khaledkorichii@gmail.com';
export const SUPPORT_WHATSAPP = '34642377474'; // digits only with country code, e.g. '34600000000'. Empty hides the button.

// Destinations shown first on the home screen (two-letter country codes).
export const POPULAR = ['es', 'tr', 'ae', 'us', 'fr', 'it', 'gb', 'jp'];

export const CURRENCY = 'EUR';
