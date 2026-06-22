const searchForm = document.querySelector("[data-api-search-form]");
const searchUrlOutput = document.querySelector("[data-api-search-url]");
const healthForm = document.querySelector("[data-api-health-form]");
const healthUrlOutput = document.querySelector("[data-api-health-url]");
const streamStartButton = document.querySelector("[data-health-stream-start]");
const streamStopButton = document.querySelector("[data-health-stream-stop]");
let healthStream;

function absoluteUrl(path) {
    return new URL(path, window.location.origin).toString();
}

function resultFor(target) {
    return document.querySelector(`#${target}`);
}

function showResult(target, status, body) {
    const result = resultFor(target);
    if (!result) {
        return;
    }
    result.hidden = false;
    result.querySelector("[data-api-result-status]").textContent = status;
    result.querySelector("[data-api-result-body]").textContent = typeof body === "string"
        ? body
        : JSON.stringify(body, null, 2);
}

async function copyText(value) {
    if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        return;
    }
    const input = document.createElement("textarea");
    input.value = value;
    input.setAttribute("readonly", "");
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    input.remove();
}

async function copyUrl(button, url) {
    const originalLabel = button.textContent;
    try {
        await copyText(url);
        button.textContent = "コピーしました";
    } catch (error) {
        button.textContent = "コピー失敗";
    }
    window.setTimeout(() => {
        button.textContent = originalLabel;
    }, 1600);
}

async function runRequest(url, target) {
    try {
        const response = await fetch(url, { cache: "no-store" });
        const contentType = response.headers.get("content-type") || "未指定";
        const body = contentType.includes("application/json")
            ? await response.json()
            : await response.text();
        showResult(target, `${response.status} ${response.statusText} / Content-Type: ${contentType}`, body);
    } catch (error) {
        showResult(target, "リクエスト失敗", { error: error.message });
    }
}

function searchUrl() {
    const query = new URLSearchParams();
    new FormData(searchForm).forEach((value, key) => {
        if (value) {
            query.set(key, value);
        }
    });
    const path = "/api/sensor-data/search";
    return absoluteUrl(query.size ? `${path}?${query}` : path);
}

function healthUrl() {
    const query = new URLSearchParams();
    new FormData(healthForm).forEach((value, key) => {
        if (value) {
            query.set(key, value);
        }
    });
    const path = "/api/health";
    return absoluteUrl(query.size ? `${path}?${query}` : path);
}

function renderSearchUrl() {
    searchUrlOutput.textContent = searchUrl();
}

function renderHealthUrl() {
    healthUrlOutput.textContent = healthUrl();
}

document.querySelectorAll("[data-api-url]").forEach((output) => {
    output.textContent = absoluteUrl(output.dataset.apiUrl);
});

document.querySelectorAll("[data-copy-api-url]").forEach((button) => {
    button.addEventListener("click", () => copyUrl(button, absoluteUrl(button.dataset.copyApiUrl)));
});

document.querySelectorAll("[data-api-request]").forEach((button) => {
    button.addEventListener("click", () => runRequest(button.dataset.apiRequest, button.dataset.apiResultTarget));
});

searchForm.addEventListener("input", renderSearchUrl);
searchForm.addEventListener("change", renderSearchUrl);
searchForm.addEventListener("submit", (event) => {
    event.preventDefault();
    runRequest(searchUrl(), searchForm.dataset.apiResultTarget);
});
document.querySelector("[data-copy-api-search-url]").addEventListener("click", (event) => {
    copyUrl(event.currentTarget, searchUrl());
});
renderSearchUrl();

healthForm.addEventListener("input", renderHealthUrl);
healthForm.addEventListener("submit", (event) => {
    event.preventDefault();
    runRequest(healthUrl(), healthForm.dataset.apiResultTarget);
});
document.querySelector("[data-copy-api-health-url]").addEventListener("click", (event) => {
    copyUrl(event.currentTarget, healthUrl());
});
renderHealthUrl();

streamStartButton.addEventListener("click", () => {
    if (healthStream) {
        return;
    }
    healthStream = new EventSource("/api/health/stream");
    healthStream.addEventListener("open", () => {
        showResult("health-stream-result", "SSE 接続済み / Content-Type: text/event-stream", { connected: true });
        streamStartButton.disabled = true;
        streamStopButton.disabled = false;
    });
    healthStream.addEventListener("health", () => {
        showResult("health-stream-result", "SSE health イベントを受信", { event: "health", data: "updated" });
    });
    healthStream.addEventListener("error", () => {
        showResult("health-stream-result", "SSE 接続エラーまたは再接続待機中", { connected: false });
    });
});

streamStopButton.addEventListener("click", () => {
    healthStream?.close();
    healthStream = undefined;
    streamStartButton.disabled = false;
    streamStopButton.disabled = true;
    showResult("health-stream-result", "SSE 切断済み", { connected: false });
});
