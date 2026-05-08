
const BACKENDS = {
  ec2:    "http://34.232.160.138",
  ecs:    "http://100.26.238.109",
  lambda: "https://8f7ddpjckd.execute-api.us-east-1.amazonaws.com/prod",
};

let activeBackend = localStorage.getItem("backend") || "lambda";

function getBaseUrl() {
  return BACKENDS[activeBackend];
}

document.addEventListener("DOMContentLoaded", () => {
  const sel = document.getElementById("backend-select");
  if (!sel) return;
  sel.value = activeBackend;
  sel.addEventListener("change", () => {
    activeBackend = sel.value;
    localStorage.setItem("backend", activeBackend);
  });
});

const API = (() => {

  async function request(method, path, body = null, params = null) {
    let url = getBaseUrl() + path;

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

  async function login(email, password) {
    return request("POST", "/login", { email, password });
  }

  async function register(email, user_name, password) {
    return request("POST", "/register", { email, user_name, password });
  }

  async function queryMusic({ title = "", artist = "", year = "", album = "" } = {}) {
    return request("GET", "/music", null, { title, artist, year, album });
  }

  async function getSubscriptions(email) {
    return request("GET", "/subscriptions", null, { email });
  }

  async function subscribe(email, song) {
    return request("POST", "/subscriptions", { email, ...song });
  }

  async function unsubscribe(email, title, artist) {
    return request("DELETE", "/subscriptions", { email, title, artist });
  }

  return { login, register, queryMusic, getSubscriptions, subscribe, unsubscribe };
})();
