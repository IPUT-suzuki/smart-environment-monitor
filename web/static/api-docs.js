const searchForm = document.querySelector("[data-api-search-form]");
const searchUrlOutput = document.querySelector("[data-api-search-url]");
const healthForm = document.querySelector("[data-api-health-form]");
const healthUrlOutput = document.querySelector("[data-api-health-url]");
const downloadUrlOutput = document.querySelector("[data-api-download-url]");
const healthDownloadForm = document.querySelector("[data-health-download-form]");
const healthDownloadUrlOutput = document.querySelector("[data-health-download-url]");
const streamStartButton = document.querySelector("[data-health-stream-start]");
const streamStopButton = document.querySelector("[data-health-stream-stop]");
const streamIndicator = document.querySelector("[data-stream-indicator]");
const toast = document.querySelector("[data-api-toast]");

let healthStream;
let toastTimer;

function absoluteUrl(path) {
    return new URL(path, window.location.origin).toString();
}

function resultFor(target) {
    return target ? document.getElementById(target) : null;
}

function showResult(target, status, body) {
    const result = resultFor(target);
    if (!result) {
        return;
    }

    result.hidden = false;
    const statusOutput = result.querySelector("[data-api-result-status]");
    const bodyOutput = result.querySelector("[data-api-result-body]");
    if (statusOutput) {
        statusOutput.textContent = status;
    }
    if (bodyOutput) {
        bodyOutput.textContent = typeof body === "string"
            ? body
            : JSON.stringify(body, null, 2);
    }
}

function showToast(message, state = "success") {
    if (!toast) {
        return;
    }
    window.clearTimeout(toastTimer);
    toast.textContent = message;
    toast.dataset.state = state;
    toast.hidden = false;
    toastTimer = window.setTimeout(() => {
        toast.hidden = true;
    }, 1800);
}

async function copyText(value) {
    if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
        return;
    }

    const input = document.createElement("textarea");
    input.value = value;
    input.setAttribute("readonly", "");
    input.style.position = "fixed";
    input.style.opacity = "0";
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    input.remove();
}

async function copyValue(value) {
    try {
        await copyText(value);
        showToast("クリップボードにコピーしました");
    } catch (error) {
        showToast("コピーできませんでした", "error");
    }
}

function queryUrl(form, path) {
    const query = new URLSearchParams();
    if (form) {
        new FormData(form).forEach((value, key) => {
            const normalized = typeof value === "string" ? value.trim() : value;
            if (normalized !== "") {
                query.set(key, normalized);
            }
        });
    }
    return absoluteUrl(query.size ? `${path}?${query.toString()}` : path);
}

function searchUrl(path = "/api/sensor-data/search") {
    return queryUrl(searchForm, path);
}

function healthUrl() {
    return queryUrl(healthForm, "/api/health");
}

function healthDownloadUrl() {
    const input = healthDownloadForm?.elements.namedItem("client_id");
    const clientId = typeof input?.value === "string" ? input.value.trim() : "";
    const encodedClientId = encodeURIComponent(clientId || "<client_id>");
    return absoluteUrl(`/api/health/${encodedClientId}/download`);
}

function renderSearchUrls() {
    if (searchUrlOutput) {
        searchUrlOutput.textContent = searchUrl();
    }
    if (downloadUrlOutput) {
        downloadUrlOutput.textContent = searchUrl("/api/sensor-data/download");
    }
}

function renderHealthUrl() {
    if (healthUrlOutput) {
        healthUrlOutput.textContent = healthUrl();
    }
}

function renderHealthDownloadUrl() {
    if (healthDownloadUrlOutput) {
        healthDownloadUrlOutput.textContent = healthDownloadUrl();
    }
}

function requestUrlFor(button) {
    const url = new URL(button.dataset.apiRequest, window.location.origin);
    const toggleTarget = button.dataset.apiWriteToggleTarget;
    if (!toggleTarget) {
        return url.toString();
    }

    const writeToggle = document.getElementById(toggleTarget);
    if (!writeToggle?.checked) {
        url.searchParams.set("dry_run", "true");
        return url.toString();
    }

    const confirmed = window.confirm(
        "実データへ登録します。CSVや端末の最新状態が更新されます。続行しますか？",
    );
    return confirmed ? url.toString() : null;
}

function syncWriteToggle(toggle) {
    const button = document.querySelector(
        `[data-api-write-toggle-target="${toggle.id}"]`,
    );
    const safeMode = toggle.closest("[data-api-safe-mode]");
    const status = safeMode?.querySelector("[data-api-write-mode-status]");
    const writeEnabled = toggle.checked;

    if (safeMode) {
        safeMode.dataset.state = writeEnabled ? "write" : "safe";
    }
    if (status) {
        status.textContent = writeEnabled
            ? "実登録モード・データ更新あり"
            : "検証のみ・保存なし";
    }
    if (button) {
        button.dataset.writeEnabled = String(writeEnabled);
        button.textContent = writeEnabled
            ? button.dataset.writeLabel
            : button.dataset.safeLabel;
    }
}

async function runRequest(button) {
    const method = (button.dataset.apiMethod || "GET").toUpperCase();
    const target = button.dataset.apiResultTarget;
    const options = {
        method,
        cache: "no-store",
        headers: {
            Accept: "application/json",
        },
    };

    if (button.dataset.apiBodyTarget) {
        const bodyInput = document.getElementById(button.dataset.apiBodyTarget);
        try {
            const parsedBody = JSON.parse(bodyInput?.value || "");
            options.headers["Content-Type"] = "application/json";
            options.body = JSON.stringify(parsedBody);
        } catch (error) {
            showResult(target, "送信前エラー", {
                error: `JSONの形式が正しくありません: ${error.message}`,
            });
            return;
        }
    }

    const requestUrl = requestUrlFor(button);
    if (!requestUrl) {
        return;
    }

    const originalLabel = button.textContent;
    button.disabled = true;
    button.textContent = "通信中…";

    try {
        const response = await fetch(requestUrl, options);
        const contentType = response.headers.get("content-type") || "未指定";
        const body = contentType.includes("application/json")
            ? await response.json()
            : await response.text();
        showResult(
            target,
            `${response.status} ${response.statusText} / Content-Type: ${contentType}`,
            body,
        );
    } catch (error) {
        showResult(target, "リクエスト失敗", { error: error.message });
    } finally {
        button.disabled = false;
        button.textContent = originalLabel;
        const toggle = button.dataset.apiWriteToggleTarget
            ? document.getElementById(button.dataset.apiWriteToggleTarget)
            : null;
        if (toggle) {
            syncWriteToggle(toggle);
        }
    }
}

document.querySelectorAll("[data-api-url]").forEach((output) => {
    output.textContent = absoluteUrl(output.dataset.apiUrl);
});

document.querySelectorAll("[data-copy-value]").forEach((button) => {
    button.addEventListener("click", () => copyValue(button.dataset.copyValue));
});

document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", () => {
        const target = document.getElementById(button.dataset.copyTarget);
        if (target) {
            copyValue(target.textContent);
        }
    });
});

document.querySelectorAll("[data-copy-api-url]").forEach((button) => {
    button.addEventListener("click", () => copyValue(absoluteUrl(button.dataset.copyApiUrl)));
});

document.querySelectorAll("[data-copy-result]").forEach((button) => {
    button.addEventListener("click", () => {
        const body = button.closest("[data-api-result]")?.querySelector("[data-api-result-body]");
        if (body) {
            copyValue(body.textContent);
        }
    });
});

document.querySelectorAll("[data-api-request]").forEach((button) => {
    button.addEventListener("click", () => runRequest(button));
});

document.querySelectorAll("[data-api-write-toggle]").forEach((toggle) => {
    toggle.addEventListener("change", () => syncWriteToggle(toggle));
    syncWriteToggle(toggle);
});

document.querySelectorAll("[data-format-json]").forEach((button) => {
    button.addEventListener("click", () => {
        const editor = document.getElementById(button.dataset.formatJson);
        try {
            editor.value = JSON.stringify(JSON.parse(editor.value), null, 2);
            showToast("JSONを整形しました");
        } catch (error) {
            showToast("JSONの形式が正しくありません", "error");
        }
    });
});

if (searchForm) {
    searchForm.addEventListener("input", renderSearchUrls);
    searchForm.addEventListener("change", renderSearchUrls);
    searchForm.addEventListener("reset", () => window.setTimeout(renderSearchUrls));
    searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const button = event.submitter;
        const originalLabel = button?.textContent;
        if (button) {
            button.disabled = true;
            button.textContent = "通信中…";
        }
        fetch(searchUrl(), { cache: "no-store", headers: { Accept: "application/json" } })
            .then(async (response) => {
                const body = await response.json();
                showResult(
                    searchForm.dataset.apiResultTarget,
                    `${response.status} ${response.statusText} / Content-Type: ${response.headers.get("content-type") || "未指定"}`,
                    body,
                );
            })
            .catch((error) => {
                showResult(searchForm.dataset.apiResultTarget, "リクエスト失敗", { error: error.message });
            })
            .finally(() => {
                if (button) {
                    button.disabled = false;
                    button.textContent = originalLabel;
                }
            });
    });
}

document.querySelector("[data-copy-api-search-url]")?.addEventListener("click", () => {
    copyValue(searchUrl());
});

document.querySelector("[data-copy-api-download-url]")?.addEventListener("click", () => {
    copyValue(searchUrl("/api/sensor-data/download"));
});

document.querySelector("[data-api-download]")?.addEventListener("click", () => {
    window.location.assign(searchUrl("/api/sensor-data/download"));
});

if (healthForm) {
    healthForm.addEventListener("input", renderHealthUrl);
    healthForm.addEventListener("change", renderHealthUrl);
    healthForm.addEventListener("reset", () => window.setTimeout(renderHealthUrl));
    healthForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const button = event.submitter;
        const originalLabel = button?.textContent;
        if (button) {
            button.disabled = true;
            button.textContent = "通信中…";
        }
        fetch(healthUrl(), { cache: "no-store", headers: { Accept: "application/json" } })
            .then(async (response) => {
                const body = await response.json();
                showResult(
                    healthForm.dataset.apiResultTarget,
                    `${response.status} ${response.statusText} / Content-Type: ${response.headers.get("content-type") || "未指定"}`,
                    body,
                );
            })
            .catch((error) => {
                showResult(healthForm.dataset.apiResultTarget, "リクエスト失敗", { error: error.message });
            })
            .finally(() => {
                if (button) {
                    button.disabled = false;
                    button.textContent = originalLabel;
                }
            });
    });
}

document.querySelector("[data-copy-api-health-url]")?.addEventListener("click", () => {
    copyValue(healthUrl());
});

if (healthDownloadForm) {
    healthDownloadForm.addEventListener("input", renderHealthDownloadUrl);
    healthDownloadForm.addEventListener("submit", (event) => {
        event.preventDefault();
        if (healthDownloadForm.reportValidity()) {
            window.location.assign(healthDownloadUrl());
        }
    });
}

document.querySelector("[data-copy-health-download-url]")?.addEventListener("click", () => {
    copyValue(healthDownloadUrl());
});

function setStreamState(state, label) {
    if (streamIndicator) {
        streamIndicator.dataset.state = state;
        streamIndicator.textContent = label;
    }
}

streamStartButton?.addEventListener("click", () => {
    if (healthStream) {
        return;
    }

    setStreamState("connecting", "接続中");
    healthStream = new EventSource("/api/health/stream");
    healthStream.addEventListener("open", () => {
        showResult("health-stream-result", "SSE 接続済み / Content-Type: text/event-stream", {
            connected: true,
        });
        setStreamState("connected", "接続中");
        streamStartButton.disabled = true;
        streamStopButton.disabled = false;
    });
    healthStream.addEventListener("health", (event) => {
        showResult("health-stream-result", "SSE healthイベントを受信", {
            event: "health",
            data: event.data,
        });
    });
    healthStream.addEventListener("error", () => {
        showResult("health-stream-result", "SSE 接続エラーまたは再接続待機中", {
            connected: false,
        });
        setStreamState("error", "再接続待機");
    });
});

streamStopButton?.addEventListener("click", () => {
    healthStream?.close();
    healthStream = undefined;
    streamStartButton.disabled = false;
    streamStopButton.disabled = true;
    setStreamState("stopped", "停止中");
    showResult("health-stream-result", "SSE 切断済み", { connected: false });
});

const navLinks = [...document.querySelectorAll(".api-sidebar a[href^='#']")];
const observedSections = navLinks
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

if ("IntersectionObserver" in window && observedSections.length) {
    const observer = new IntersectionObserver((entries) => {
        const visible = entries
            .filter((entry) => entry.isIntersecting)
            .sort((left, right) => right.intersectionRatio - left.intersectionRatio)[0];
        if (!visible) {
            return;
        }
        navLinks.forEach((link) => {
            link.classList.toggle("is-active", link.getAttribute("href") === `#${visible.target.id}`);
        });
    }, {
        rootMargin: "-15% 0px -70% 0px",
        threshold: [0, 0.2, 0.6],
    });
    observedSections.forEach((section) => observer.observe(section));
}

renderSearchUrls();
renderHealthUrl();
renderHealthDownloadUrl();
