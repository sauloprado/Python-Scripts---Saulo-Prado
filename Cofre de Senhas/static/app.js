const state = {
    unlocked: false,
    vaultExists: false,
    entries: [],
    editingId: null,
    icons: [],
    duplicateGroups: [],
    categories: [],
    activeCategory: "Todas",
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
    importForm: document.querySelector("#import-form"),
    entriesList: document.querySelector("#entries-list"),
    duplicatesList: document.querySelector("#duplicates-list"),
    categoryFilterBar: document.querySelector("#category-filter-bar"),
    searchInput: document.querySelector("#search-input"),
    generateButton: document.querySelector("#generate-button"),
    lockButton: document.querySelector("#lock-button"),
    formTitle: document.querySelector("#form-title"),
    formSubtitle: document.querySelector("#form-subtitle"),
    saveButton: document.querySelector("#save-button"),
    cancelEditButton: document.querySelector("#cancel-edit-button"),
    iconOverrideSelect: document.querySelector("#icon-override-select"),
    categoryOptions: document.querySelector("#category-options"),
    toast: document.querySelector("#toast"),
};

const MASK = "************";
const revealTimers = new Map();

function duplicateKey(entry) {
    return [
        (entry.category || "Geral").trim().toLowerCase(),
        (entry.service || "").trim().toLowerCase(),
        (entry.username || "").trim().toLowerCase(),
        (entry.url || "").trim().toLowerCase(),
    ].join("||");
}

function buildDuplicateMap(entries) {
    const counts = new Map();
    for (const entry of entries) {
        const key = duplicateKey(entry);
        counts.set(key, (counts.get(key) || 0) + 1);
    }
    return counts;
}

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

function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
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

    const duplicates = state.duplicateGroups.length;
    elements.status.textContent = "Cofre desbloqueado";
    elements.subtitle.textContent = duplicates
        ? `${state.entries.length} item(ns) protegidos(s). Ha grupos duplicados para revisar.`
        : `${state.entries.length} item(ns) protegido(s) no armazenamento local criptografado.`;
}

function renderIconOptions() {
    if (!elements.iconOverrideSelect) {
        return;
    }

    const currentValue = elements.iconOverrideSelect.value;
    elements.iconOverrideSelect.innerHTML = [
        `<option value="">Automatico</option>`,
        ...state.icons.map((icon) => `<option value="${escapeHtml(icon.key)}">${escapeHtml(icon.key)}</option>`),
    ].join("");
    elements.iconOverrideSelect.value = currentValue || "";
}

function renderCategoryOptions() {
    if (!elements.categoryOptions) {
        return;
    }

    elements.categoryOptions.innerHTML = state.categories
        .map((category) => `<option value="${escapeHtml(category)}"></option>`)
        .join("");
}

function renderCategoryFilters() {
    if (!elements.categoryFilterBar) {
        return;
    }

    const counts = new Map();
    for (const entry of state.entries) {
        const category = entry.category || "Geral";
        counts.set(category, (counts.get(category) || 0) + 1);
    }

    const categories = ["Todas", ...Array.from(counts.keys()).sort((a, b) => a.localeCompare(b))];
    elements.categoryFilterBar.innerHTML = categories.map((category) => {
        const count = category === "Todas" ? state.entries.length : (counts.get(category) || 0);
        const active = state.activeCategory === category ? "is-active" : "";
        return `
            <button type="button" class="category-chip ${active}" data-category-filter="${escapeHtml(category)}">
                <span>${escapeHtml(category)}</span>
                <strong>${count}</strong>
            </button>
        `;
    }).join("");
}

function renderDuplicateGroups() {
    if (!elements.duplicatesList) {
        return;
    }

    if (!state.duplicateGroups.length) {
        elements.duplicatesList.innerHTML = `<div class="duplicate-card"><p class="entry-meta">Nenhum grupo duplicado encontrado.</p></div>`;
        renderLayout();
        return;
    }

    elements.duplicatesList.innerHTML = state.duplicateGroups.map((group) => `
        <article class="duplicate-card">
            <div class="duplicate-head">
                <div>
                    <strong>${group.count} itens duplicados</strong>
                    <p class="entry-meta">${escapeHtml(group.entries[0].category)} / ${escapeHtml(group.entries[0].service)} / ${escapeHtml(group.entries[0].username)}</p>
                </div>
                <button class="danger compact" type="button" data-remove-duplicates="${escapeHtml(group.key)}">Remover duplicados</button>
            </div>
            <div class="duplicate-items">
                ${group.entries.map((entry, index) => `
                    <div class="duplicate-item ${index === 0 ? "is-kept" : ""}">
                        <span>${index === 0 ? "Mantido" : "Removivel"}</span>
                        <strong>${escapeHtml(entry.service)}</strong>
                        <small>${escapeHtml(entry.username)}${entry.url ? ` • ${escapeHtml(entry.url)}` : ""}</small>
                    </div>
                `).join("")}
            </div>
        </article>
    `).join("");

    renderLayout();
}

function renderEntries() {
    const search = elements.searchInput.value.trim().toLowerCase();
    const duplicateMap = buildDuplicateMap(state.entries);
    const filtered = state.entries.filter((entry) => {
        const categoryMatch = state.activeCategory === "Todas" || entry.category === state.activeCategory;
        const textMatch = (
            entry.category.toLowerCase().includes(search) ||
            entry.service.toLowerCase().includes(search) ||
            entry.username.toLowerCase().includes(search)
        );
        return (
            categoryMatch && textMatch
        );
    });

    if (!filtered.length) {
        elements.entriesList.innerHTML = `<div class="entry-card"><p class="entry-meta">Nenhuma credencial encontrada.</p></div>`;
        renderLayout();
        return;
    }

    elements.entriesList.innerHTML = filtered.map((entry) => `
        <article class="entry-card ${duplicateMap.get(duplicateKey(entry)) > 1 ? "is-duplicate" : ""}">
            <div class="entry-head">
                <div class="entry-icon" style="background:${escapeHtml(entry.icon.bg)};color:${escapeHtml(entry.icon.fg)};">
                    ${entry.icon.image_url
                        ? `<img src="${escapeHtml(entry.icon.image_url)}" alt="${escapeHtml(entry.service)}" class="entry-icon-image" loading="lazy" onerror="this.style.display='none'; this.nextElementSibling.style.display='inline-flex';">`
                        : ""}
                    <span class="entry-icon-fallback" style="${entry.icon.image_url ? "display:none;" : ""}">
                        ${escapeHtml(entry.icon.glyph)}
                    </span>
                </div>
                <div class="entry-head-copy">
                    <div class="entry-category">${escapeHtml(entry.category)}</div>
                    <h4>${escapeHtml(entry.service)}</h4>
                    ${duplicateMap.get(duplicateKey(entry)) > 1 ? `<div class="entry-warning">Duplicado detectado</div>` : ""}
                </div>
            </div>
            <p class="entry-meta"><strong>Usuario:</strong> ${escapeHtml(entry.username)}</p>
            ${entry.url ? `<p class="entry-meta"><strong>URL:</strong> <a href="${escapeHtml(entry.url)}" target="_blank" rel="noreferrer">${escapeHtml(entry.url)}</a></p>` : ""}
            <div class="entry-secret-row">
                <div class="entry-password is-hidden" data-password="${entry.id}" data-secret="${escapeHtml(entry.password)}">${MASK}</div>
                <button class="ghost compact icon-button" type="button" data-toggle="${entry.id}" aria-label="Mostrar ou ocultar senha">Ver</button>
                <button class="ghost compact icon-button" type="button" data-copy="${entry.id}" aria-label="Copiar senha">Copiar</button>
            </div>
            ${entry.notes ? `<p class="entry-notes">${escapeHtml(entry.notes)}</p>` : ""}
            <div class="entry-actions">
                <button class="ghost compact" type="button" data-edit="${entry.id}">Editar</button>
                <button class="danger compact" type="button" data-delete="${entry.id}">Excluir</button>
            </div>
        </article>
    `).join("");

    renderCategoryFilters();
    renderLayout();
}

function resetEntryForm() {
    state.editingId = null;
    elements.entryForm.reset();
    elements.entryForm.querySelector("[name='entry_id']").value = "";
    elements.entryForm.querySelector("[name='category']").value = "Geral";
    elements.entryForm.querySelector("[name='icon_override']").value = "";
    elements.formTitle.textContent = "Nova entrada";
    elements.formSubtitle.textContent = "Adicione um servico ao cofre local com categoria, URL e observacoes.";
    elements.saveButton.textContent = "Salvar credencial";
    elements.cancelEditButton.classList.add("hidden");
}

function preencherFormularioParaEdicao(entry) {
    state.editingId = entry.id;
    elements.entryForm.querySelector("[name='entry_id']").value = entry.id;
    elements.entryForm.querySelector("[name='category']").value = entry.category || "Geral";
    elements.entryForm.querySelector("[name='icon_override']").value = entry.icon_override || "";
    elements.entryForm.querySelector("[name='service']").value = entry.service;
    elements.entryForm.querySelector("[name='username']").value = entry.username;
    elements.entryForm.querySelector("[name='password']").value = entry.password;
    elements.entryForm.querySelector("[name='url']").value = entry.url || "";
    elements.entryForm.querySelector("[name='notes']").value = entry.notes || "";
    elements.formTitle.textContent = "Editar entrada";
    elements.formSubtitle.textContent = "Atualize os dados da credencial selecionada.";
    elements.saveButton.textContent = "Salvar alteracoes";
    elements.cancelEditButton.classList.remove("hidden");
    elements.entryForm.scrollIntoView({ behavior: "smooth", block: "start" });
}

function ocultarSenha(entryId) {
    const passwordNode = elements.entriesList.querySelector(`[data-password="${entryId}"]`);
    const toggleButton = elements.entriesList.querySelector(`[data-toggle="${entryId}"]`);
    const card = toggleButton?.closest(".entry-card");

    if (!passwordNode || !toggleButton) {
        return;
    }

    passwordNode.classList.add("is-hidden");
    passwordNode.textContent = MASK;
    toggleButton.textContent = "Ver";
    card?.classList.remove("is-revealed");

    const timer = revealTimers.get(entryId);
    if (timer) {
        window.clearTimeout(timer);
        revealTimers.delete(entryId);
    }
}

function revelarSenha(entryId) {
    const passwordNode = elements.entriesList.querySelector(`[data-password="${entryId}"]`);
    const toggleButton = elements.entriesList.querySelector(`[data-toggle="${entryId}"]`);
    const card = toggleButton?.closest(".entry-card");

    if (!passwordNode || !toggleButton) {
        return;
    }

    passwordNode.classList.remove("is-hidden");
    passwordNode.textContent = passwordNode.getAttribute("data-secret");
    toggleButton.textContent = "Ocultar";
    card?.classList.add("is-revealed");

    const previousTimer = revealTimers.get(entryId);
    if (previousTimer) {
        window.clearTimeout(previousTimer);
    }

    const timer = window.setTimeout(() => {
        ocultarSenha(entryId);
        showToast("Senha ocultada novamente.");
    }, 8000);

    revealTimers.set(entryId, timer);
}

async function loadIcons() {
    const data = await requestJson("/api/icons");
    state.icons = data.icons;
    renderIconOptions();
}

async function loadCategories() {
    const data = await requestJson("/api/categories");
    state.categories = data.categories;
    renderCategoryOptions();
}

async function loadStatus() {
    const data = await requestJson("/api/status");
    state.vaultExists = data.vault_exists;
    state.unlocked = data.unlocked;

    if (state.unlocked) {
        await Promise.all([loadEntries(), loadDuplicates()]);
    } else {
        renderLayout();
    }
}

async function loadEntries() {
    const data = await requestJson("/api/entries");
    state.entries = data.entries;
    renderEntries();
}

async function loadDuplicates() {
    const data = await requestJson("/api/duplicates");
    state.duplicateGroups = data.groups;
    renderDuplicateGroups();
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
        await Promise.all([loadIcons(), loadCategories(), loadDuplicates()]);
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
        await Promise.all([loadIcons(), loadCategories(), loadEntries(), loadDuplicates()]);
        showToast("Cofre desbloqueado.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.entryForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(elements.entryForm);
    const payload = Object.fromEntries(formData.entries());
    const entryId = payload.entry_id;
    try {
        const data = await requestJson(entryId ? `/api/entries/${entryId}` : "/api/entries", {
            method: entryId ? "PUT" : "POST",
            body: JSON.stringify(payload),
        });

        if (entryId) {
            state.entries = state.entries.map((entry) => entry.id === entryId ? data.entry : entry);
            showToast("Credencial atualizada com sucesso.");
        } else {
            state.entries.push(data.entry);
            showToast("Credencial salva com sucesso.");
        }

        resetEntryForm();
        renderEntries();
        await loadDuplicates();
    } catch (error) {
        showToast(error.message);
    }
});

elements.importForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(elements.importForm);
    try {
        const data = await requestJson("/api/import", {
            method: "POST",
            body: JSON.stringify(Object.fromEntries(formData.entries())),
        });
        state.entries.push(...data.entries);
        elements.importForm.reset();
        elements.importForm.querySelector("[name='default_category']").value = "Importados";
        renderEntries();
        await loadDuplicates();
        showToast(
            data.skipped_duplicates
                ? `${data.count} importado(s) e ${data.skipped_duplicates} duplicado(s) ignorado(s).`
                : `${data.count} cadastro(s) importado(s) com sucesso.`
        );
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
        state.duplicateGroups = [];
        resetEntryForm();
        renderLayout();
        renderDuplicateGroups();
        showToast("Cofre bloqueado.");
    } catch (error) {
        showToast(error.message);
    }
});

elements.cancelEditButton.addEventListener("click", () => {
    resetEntryForm();
});

elements.searchInput.addEventListener("input", renderEntries);

elements.categoryFilterBar.addEventListener("click", (event) => {
    const category = event.target.closest("[data-category-filter]")?.getAttribute("data-category-filter");
    if (!category) {
        return;
    }
    state.activeCategory = category;
    renderEntries();
});

elements.entriesList.addEventListener("click", async (event) => {
    const copyId = event.target.getAttribute("data-copy");
    const deleteId = event.target.getAttribute("data-delete");
    const toggleId = event.target.getAttribute("data-toggle");
    const editId = event.target.getAttribute("data-edit");

    if (toggleId) {
        const passwordNode = elements.entriesList.querySelector(`[data-password="${toggleId}"]`);
        if (!passwordNode) {
            return;
        }

        if (passwordNode.classList.contains("is-hidden")) {
            revelarSenha(toggleId);
        } else {
            ocultarSenha(toggleId);
        }
        return;
    }

    if (copyId) {
        const entry = state.entries.find((item) => item.id === copyId);
        if (!entry) {
            return;
        }
        await navigator.clipboard.writeText(entry.password);
        showToast(`Senha copiada: ${entry.service}.`);
        return;
    }

    if (editId) {
        const entry = state.entries.find((item) => item.id === editId);
        if (!entry) {
            return;
        }
        preencherFormularioParaEdicao(entry);
        showToast(`Editando: ${entry.service}.`);
        return;
    }

    if (deleteId) {
        try {
            await requestJson(`/api/entries/${deleteId}`, { method: "DELETE" });
            state.entries = state.entries.filter((item) => item.id !== deleteId);
            if (state.editingId === deleteId) {
                resetEntryForm();
            }
            renderEntries();
            await loadDuplicates();
            showToast("Entrada removida.");
        } catch (error) {
            showToast(error.message);
        }
    }
});

elements.duplicatesList.addEventListener("click", async (event) => {
    const groupKey = event.target.getAttribute("data-remove-duplicates");
    if (!groupKey) {
        return;
    }

    try {
        const data = await requestJson("/api/duplicates/remove", {
            method: "POST",
            body: JSON.stringify({ group_key: groupKey }),
        });
        await Promise.all([loadEntries(), loadDuplicates()]);
        showToast(`${data.removed_count} duplicado(s) removido(s).`);
    } catch (error) {
        showToast(error.message);
    }
});

Promise.all([loadIcons().catch(() => {}), loadCategories().catch(() => {}), loadStatus()])
    .catch((error) => {
        showToast(error.message);
    });
