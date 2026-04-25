async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || "Falha ao processar a requisicao.");
  }

  return data;
}

export function getSession() {
  return request("/api/auth/me");
}

export function login(username, password) {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export function logout() {
  return request("/api/auth/logout", { method: "POST" });
}

export function getLatestNews() {
  return request("/api/news");
}

export function generateNews(payload) {
  return request("/api/news/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getRuns() {
  return request("/api/runs");
}
