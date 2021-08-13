/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-kcyr46o1.us', // the auth0 domain prefix
    audience: 'https://ahhsn.com/apps/coffee-shop', // the audience set for the auth0 app
    clientId: 'PYX8x1N7053i4MS65WEhchWQZM8yh1p1', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application. 
  }
};
