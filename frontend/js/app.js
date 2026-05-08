

const EC2_URL    = "http://34.232.160.138";
const ECS_URL    = "http://18.235.243.92";
const LAMBDA_URL = "https://8f7ddpjckd.execute-api.us-east-1.amazonaws.com/prod";

const BASE_URL = LAMBDA_URL;

const API = (() => {

  async function request(method, path, body = null, params = null) {
    let url = BASE_URL + path;

    if (params) {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== "" && v !== null && v !== undefined)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join("&");
      if (qs) url += "?" + qs;
    }

    const options = {
      method,
      headers: { "Content-Type": "application/json" },
    };
    if (body) options.body = JSON.stringify(body);

    const res = await fetch(url, options);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw Object.assign(new Error(data.message || "Request failed"), { status: res.status, data });
    }
    return data;
  }

  //  Auth 
  //  POST /login
   
  async function login(email, password) {
    return request("POST", "/login", { email, password });
  }

  // POST /register
  async function register(email, user_name, password) {
    return request("POST", "/register", { email, user_name, password });
  }

  //  Music 
  // Get /music
  async function queryMusic({ title = "", artist = "", year = "", album = "" } = {}) {
    return request("GET", "/music", null, { title, artist, year, album });
  }

  //  Subscriptions 
  // GET /subscriptions
  async function getSubscriptions(email) {
    return request("GET", "/subscriptions", null, { email });
  }

  // POST /subscriptions
  async function subscribe(email, song) {
    return request("POST", "/subscriptions", { email, ...song });
  }

  //DELETE /subscriptions
  async function unsubscribe(email, title, artist) {
    return request("DELETE", "/subscriptions", { email, title, artist });
  }

  return { login, register, queryMusic, getSubscriptions, subscribe, unsubscribe };
})();
