function setStatus(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    el.textContent = message;
    el.style.color = isError ? "#e74c3c" : "#2ecc71";
    el.style.fontWeight = "bold";
    el.style.textShadow =
        "-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000";
}

function downloadBlob(filename, blobParts, mimeType) {
    const blob = new Blob(blobParts, { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsArrayBuffer(file);
    });
}

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsText(file);
    });
}

// --- Chaves ---

document.getElementById("btnGenerateKeys").addEventListener("click", async () => {
    try {
        const keyPair = await dbGenerateRSAKeys();
        document.getElementById("publicKeyPem").value = keyPair.publicKey;
        document.getElementById("privateKeyPem").value = keyPair.privateKey;
        setStatus("keysStatus", "Par de chaves gerado.");
    } catch (error) {
        setStatus("keysStatus", "Erro ao gerar chaves: " + error.message, true);
    }
});

document.getElementById("btnDownloadPublicKey").addEventListener("click", () => {
    const pem = document.getElementById("publicKeyPem").value;
    if (!pem) {
        setStatus("keysStatus", "Gere ou carregue uma chave pública antes de baixar.", true);
        return;
    }
    downloadBlob("public_key.pem", [pem], "application/x-pem-file");
});

document.getElementById("btnDownloadPrivateKey").addEventListener("click", () => {
    const pem = document.getElementById("privateKeyPem").value;
    if (!pem) {
        setStatus("keysStatus", "Gere ou carregue uma chave privada antes de baixar.", true);
        return;
    }
    downloadBlob("private_key.pem", [pem], "application/x-pem-file");
});

document.getElementById("publicKeyFile").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    document.getElementById("publicKeyPem").value = await readFileAsText(file);
    setStatus("keysStatus", "Chave pública carregada de " + file.name + ".");
});

document.getElementById("privateKeyFile").addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    document.getElementById("privateKeyPem").value = await readFileAsText(file);
    setStatus("keysStatus", "Chave privada carregada de " + file.name + ".");
});

function enableKeyDragAndDrop(textareaId, label) {
    const textarea = document.getElementById(textareaId);

    textarea.addEventListener("dragover", (event) => {
        event.preventDefault();
        textarea.classList.add("drag-over");
    });

    textarea.addEventListener("dragleave", () => {
        textarea.classList.remove("drag-over");
    });

    textarea.addEventListener("drop", async (event) => {
        event.preventDefault();
        textarea.classList.remove("drag-over");
        const file = event.dataTransfer.files[0];
        if (!file) return;
        textarea.value = await readFileAsText(file);
        setStatus("keysStatus", label + " carregada de " + file.name + " (arrastar e soltar).");
    });
}

enableKeyDragAndDrop("publicKeyPem", "Chave pública");
enableKeyDragAndDrop("privateKeyPem", "Chave privada");

// --- Texto ---

document.getElementById("btnEncryptText").addEventListener("click", async () => {
    try {
        const publicKeyPem = document.getElementById("publicKeyPem").value;
        const plainText = document.getElementById("plainText").value;
        const cipherTextB64 = await dbEncryptString(plainText, publicKeyPem);
        document.getElementById("cipherTextB64").value = cipherTextB64;
        setStatus("textStatus", "Texto criptografado.");
    } catch (error) {
        setStatus("textStatus", "Erro ao criptografar: " + error.message, true);
    }
});

document.getElementById("btnDecryptText").addEventListener("click", async () => {
    try {
        const privateKeyPem = document.getElementById("privateKeyPem").value;
        const cipherTextB64 = document.getElementById("cipherTextB64").value;
        const plainText = await dbDecryptString(cipherTextB64, privateKeyPem);
        document.getElementById("plainText").value = plainText;
        setStatus("textStatus", "Texto descriptografado.");
    } catch (error) {
        setStatus("textStatus", "Erro ao descriptografar: " + error.message, true);
    }
});

// --- Arquivo / imagem ---

let lastEncryptedFileName = "arquivo";

document.getElementById("btnEncryptFile").addEventListener("click", async () => {
    try {
        const publicKeyPem = document.getElementById("publicKeyPem").value;
        const file = document.getElementById("fileToEncrypt").files[0];
        if (!file) {
            setStatus("fileStatus", "Selecione um arquivo para criptografar.", true);
            return;
        }
        const data = await readFileAsArrayBuffer(file);
        const encrypted = await dbEncryptByte(data, publicKeyPem);
        downloadBlob(file.name + ".enc", [encrypted], "application/octet-stream");
        setStatus("fileStatus", "Arquivo criptografado e baixado como " + file.name + ".enc.");
    } catch (error) {
        setStatus("fileStatus", "Erro ao criptografar arquivo: " + error.message, true);
    }
});

document.getElementById("btnDecryptFile").addEventListener("click", async () => {
    try {
        const privateKeyPem = document.getElementById("privateKeyPem").value;
        const file = document.getElementById("fileToDecrypt").files[0];
        if (!file) {
            setStatus("fileStatus", "Selecione um arquivo .enc para descriptografar.", true);
            return;
        }
        const outputName = document.getElementById("decryptedFileName").value || "arquivo_decifrado";

        const data = await readFileAsArrayBuffer(file);
        const decrypted = await dbDecryptByte(data, privateKeyPem);
        downloadBlob(outputName, [decrypted], "application/octet-stream");

        const previewImg = document.getElementById("decryptedPreview");
        const blob = new Blob([decrypted]);
        previewImg.src = URL.createObjectURL(blob);
        previewImg.style.display = "inline-block";

        setStatus("fileStatus", "Arquivo descriptografado e baixado como " + outputName + ".");
    } catch (error) {
        setStatus("fileStatus", "Erro ao descriptografar arquivo: " + error.message, true);
    }
});

// --- Usuários ---

let loadedUsers = [];

function renderUsersTable(users) {
    const tbody = document.getElementById("usersTableBody");
    tbody.innerHTML = "";

    for (const user of users) {
        const row = document.createElement("tr");
        for (const field of ["id", "name", "email", "cpf", "status"]) {
            const cell = document.createElement("td");
            const input = document.createElement("input");
            input.type = "text";
            input.readOnly = true;
            input.value = user[field];
            cell.appendChild(input);
            row.appendChild(cell);
        }
        tbody.appendChild(row);
    }
}

function csvEscape(value) {
    const str = String(value ?? "");
    if (/[",\n]/.test(str)) {
        return '"' + str.replace(/"/g, '""') + '"';
    }
    return str;
}

function usersToCsv(users) {
    const header = ["id", "name", "email", "cpf", "status"];
    const lines = [header.join(",")];
    for (const user of users) {
        lines.push(header.map((field) => csvEscape(user[field])).join(","));
    }
    return lines.join("\n");
}

async function loadUsers() {
    const response = await fetch("/users");
    if (!response.ok) {
        throw new Error("HTTP " + response.status);
    }
    loadedUsers = await response.json();
    renderUsersTable(loadedUsers);
    return loadedUsers;
}

document.getElementById("btnLoadUsers").addEventListener("click", async () => {
    try {
        const users = await loadUsers();
        setStatus("usersStatus", users.length + " usuário(s) carregado(s).");
    } catch (error) {
        setStatus("usersStatus", "Erro ao carregar usuários: " + error.message, true);
    }
});

document.getElementById("btnDownloadEncryptedCsv").addEventListener("click", () => {
    if (loadedUsers.length === 0) {
        setStatus("usersStatus", "Carregue os usuários antes de baixar o CSV.", true);
        return;
    }
    downloadBlob("usuarios_criptografados.csv", [usersToCsv(loadedUsers)], "text/csv");
    setStatus("usersStatus", "CSV criptografado baixado.");
});

document.getElementById("btnDownloadDecryptedCsv").addEventListener("click", async () => {
    if (loadedUsers.length === 0) {
        setStatus("usersStatus", "Carregue os usuários antes de baixar o CSV.", true);
        return;
    }

    const privateKeyPem = document.getElementById("privateKeyPem").value;
    if (!privateKeyPem) {
        setStatus("usersStatus", "Informe a chave privada para descriptografar os usuários.", true);
        return;
    }

    try {
        const decryptField = (value) =>
            value ? dbDecryptString(value, privateKeyPem) : Promise.resolve("");

        const decryptedUsers = [];
        for (const user of loadedUsers) {
            decryptedUsers.push({
                id: user.id,
                name: await decryptField(user.name),
                email: await decryptField(user.email),
                cpf: await decryptField(user.cpf),
                status: user.status,
            });
        }
        downloadBlob("usuarios_descriptografados.csv", [usersToCsv(decryptedUsers)], "text/csv");
        setStatus("usersStatus", "CSV descriptografado baixado.");
    } catch (error) {
        setStatus("usersStatus", "Erro ao descriptografar usuários: " + error.message, true);
    }
});

// --- Novo usuário (modal) ---

function openCreateUserModal() {
    document.getElementById("newUserId").value = crypto.randomUUID();
    document.getElementById("newUserName").value = "";
    document.getElementById("newUserEmail").value = "";
    document.getElementById("newUserCpf").value = "";
    document.getElementById("newUserStatus").value = "active";
    setStatus("createUserStatus", "");
    document.getElementById("createUserModalOverlay").classList.add("open");
}

function closeCreateUserModal() {
    document.getElementById("createUserModalOverlay").classList.remove("open");
}

document.getElementById("btnOpenCreateUserModal").addEventListener("click", openCreateUserModal);
document.getElementById("btnCancelCreateUser").addEventListener("click", closeCreateUserModal);

document.getElementById("createUserForm").addEventListener("submit", async (event) => {
    event.preventDefault();

    const publicKeyPem = document.getElementById("publicKeyPem").value;
    if (!publicKeyPem) {
        setStatus("createUserStatus", "Informe a chave pública (seção 1) para criptografar o novo usuário.", true);
        return;
    }

    const name = document.getElementById("newUserName").value;
    const email = document.getElementById("newUserEmail").value;
    const cpf = document.getElementById("newUserCpf").value;
    const status = document.getElementById("newUserStatus").value;

    try {
        const payload = {
            name: await dbEncryptString(name, publicKeyPem),
            email: await dbEncryptString(email, publicKeyPem),
            cpf: await dbEncryptString(cpf, publicKeyPem),
            status,
        };

        const response = await fetch("/users", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            throw new Error(errorBody.error || "HTTP " + response.status);
        }

        closeCreateUserModal();
        await loadUsers();
        setStatus("usersStatus", "Usuário criado com sucesso.");
    } catch (error) {
        setStatus("createUserStatus", "Erro ao criar usuário: " + error.message, true);
    }
});
