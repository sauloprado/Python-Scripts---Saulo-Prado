const state = {
    unlocked: false,
    vaultExists: false,
    entries: [],
};

const elements = {
    status: document.querySelector("#vault-status"),
    subtitle: document.querySelector("#vault-subtitle"),
    setupSection: document.querySelector("#setup-section"),
    unlockSection: document.querySelector("#unlock-section"),
    vaultSection: document.querySelector("#vault-section"),
    setupForm: document.querySelector("#setup-form"),
    unlockForm: document.querySelector("#unlock-form"),
    entryForm: document.querySelector("#entry-form"),
    entriesList: document.querySelector("#entries-list"),
    searchInput: document.querySelector("#search-input"),
    generateButton: document.querySelector("#generate-button"),
    lockButton: document.querySelector("#lock-button"),
    toast: document.querySelector("#toast"),
};

async function requestJson(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    });

    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || "Ocorreu um erro inesperado.");
    }
    return data;
}

function showToast(message) {
    elements.toast.textContent = message;
    elements.toast.classList.remove("hidden");
    window.clearTimeout(showToast.timeoutId);
    showToast.timeoutId = window.setTimeout(() => {
        elements.toast.classList.add("hidden");
    }, 3200);
}

function renderLayout() {
    elements.setupSection.classList.toggle("hidden", state.vaultExists);
    elements.unlockSection.classList.toggle("hidden", !state.vaultExists || state.unlocked);
    elements.vaultSection.classList.toggle("hidden", !state.unlocked);

    if (!state.vaultExists) {
        elements.status.textContent = "Cofre ainda nao criado";
        elements.subtitle.textContent = "Defina uma senha mestra para inicializar o cofre local.";
        return;
    }

    if (!state.unlocked) {
        elements.status.textContent = "Cofre bloqueado";
        elements.subtitle.textContent = "Desbloqueie o cofre com sua senha mestra para acessar os dados.";
        return;
    }

    elements.status.textContent = "Cofre desbloqueado";
    elements.subtitle.textContent = `${state.entries.length} item(ns) protegido(s) no armazenamento local criptografado.`;
}

function escapeHtml(value) {
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function renderEntries() {
    const search = elements.searchInput.value.trim().toLowerCase();
    const filtered = state.entries.filter((entry) => {
        return (
            entry.service.toLowerCase().includes(search) ||
            entry.username.toLowerCase().includes(search)
        );
    });

    if (!filtered.length) {
        elements.entriesList.innerHTML = `<div class="entry-card"><p class="entry-meta">Nenhuma credencial encontrada.</p></div>`;
        renderLayout();
        return;
    }

    elements.entriesList.innerHTML = filtered.map((entry) => `
        <article class="entry-card">
            <h4>${escapeHtml(entry.service)}</h4>
            <p class="entry-meta"><strong>Usuario:</strong> ${escapeHtml(entry.username)}</p>
            ${entry.url ? `<p class="entry-meta"><strong>URL:</strong> <a href="${escapeHtml(entry.url)}" target="_blank" rel="noreferrer">${escapeHtml(entry.url)}</a></p>` : ""}
            <div class="entry-password">${escapeHtml(entry.password)}</div>
            ${entry.notes ? `<p class="entry-notes">${escapeHtml(entry.notes)}</p>` : ""}
            <div class="entry-actions">
                <button class="ghost compact" type="button" data-copy="${entry.id}">Copiar senha</button>
                <button class="danger compact" type="button" data-delete="${entry.id}">Excluir</button>
            </div>
        </article>
    `).join("");

    renderLayout();
}

async function loadStatus() {
    const data = await requestJson("/api/status");
    state.vaultExists = data.vault_exists;
    state.unlocked = data.unlocked;

    if (state.unlocked) {
        await loadEntries();
    } else {
        renderLayout();
    }
}

async function loadEntries() {
    const data = await requestJson("/api/entries");
    state.entries = data.entries;
    renderEntries();
}

elements.setupForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(elements.setupForm);
    try {
        await requestJson("/api/setup", {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData.entries())),
        });
        state.vaultExists = true;
        state.unlocked = true;
        state.entries = [];
        elements.setupForm.reset();
        renderEntries();
        showToast("Cofre criado com sucesso.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.unlockForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(elements.unlockForm);
    try {
        await requestJson("/api/unlock", {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData.entries())),
        });
        state.unlocked = true;
        elements.unlockForm.reset();
        await loadEntries();
        showToast("Cofre desbloqueado.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.entryForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(elements.entryForm);
    try {
        const data = await requestJson("/api/entries", {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData.entries())),
        });
        state.entries.push(data.entry);
        elements.entryForm.reset();
        renderEntries();
        showToast("Credencial salva com sucesso.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.generateButton.addEventListener("click", async () => {
    try {
        const data = await requestJson("/api/generate-password?length=20");
        elements.entryForm.querySelector("[name='password']").value = data.password;
        showToast("Senha forte gerada.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.lockButton.addEventListener("click", async () => {
    try {
        await requestJson("/api/lock", { method: "POST", body: "{}" });
        state.unlocked = false;
        state.entries = [];
        renderLayout();
        showToast("Cofre bloqueado.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.searchInput.addEventListener("input", renderEntries);

elements.entriesList.addEventListener("click", async (event) => {
    const copyId = event.target.getAttribute("data-copy");
    const deleteId = event.target.getAttribute("data-delete");

    if (copyId) {
        const entry = state.entries.find((item) => item.id === copyId);
        if (!entry) {
            return;
        }
        await navigator.clipboard.writeText(entry.password);
        showToast(`Senha copiada: ${entry.service}.`);
        return;
    }

    if (deleteId) {
        try {
            await requestJson(`/api/entries/${deleteId}`, { method: "DELETE" });
            state.entries = state.entries.filter((item) => item.id !== deleteId);
            renderEntries();
            showToast("Entrada removida.");
        } catch (error) {
            showToast(error.message);
        }
    }
});

loadStatus().catch((error) => {
    showToast(error.message);
});
