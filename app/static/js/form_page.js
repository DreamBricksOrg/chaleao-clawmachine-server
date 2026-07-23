// --- Máscaras ---

function maskName(value) {
    return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s]/g, "");
}

function maskPhone(value) {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    if (digits.length > 10) {
        return digits.replace(/(\d{2})(\d{5})(\d{4})/, "($1) $2-$3");
    }
    if (digits.length > 6) {
        return digits.replace(/(\d{2})(\d{4})(\d{1,4})/, "($1) $2-$3");
    }
    if (digits.length > 2) {
        return digits.replace(/(\d{2})(\d{1,5})/, "($1) $2");
    }
    return digits;
}

// --- Validação ---

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
    const digits = phone.replace(/\D/g, "");
    return digits.length === 10 || digits.length === 11;
}

// --- Helpers de UI ---

function setFieldError(fieldName, message) {
    const el = document.getElementById(fieldName + "Error");
    if (el) el.textContent = message || "";
}

function setFormStatus(message, isError = false) {
    const el = document.getElementById("formStatus");
    el.textContent = message;
    el.classList.toggle("error", Boolean(isError));
    el.classList.toggle("success", !isError && Boolean(message));
}

function getUserIdFromUrl() {
    const parts = window.location.pathname.split("/").filter(Boolean);
    return parts[parts.length - 1];
}

// --- Aplicar máscaras enquanto digita ---

document.getElementById("name").addEventListener("input", (event) => {
    event.target.value = maskName(event.target.value);
});

document.getElementById("phone").addEventListener("input", (event) => {
    event.target.value = maskPhone(event.target.value);
});

// --- Envio ---

async function handleSubmit() {
    setFormStatus("");
    ["name", "email", "phone", "terms"].forEach((field) => setFieldError(field, ""));

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const phone = document.getElementById("phone").value;
    const termsChecked = document.getElementById("terms").checked;

    let valid = true;

    if (!name) {
        setFieldError("name", "Informe seu nome.");
        valid = false;
    }
    if (!isValidEmail(email)) {
        setFieldError("email", "E-mail inválido.");
        valid = false;
    }
    if (!isValidPhone(phone)) {
        setFieldError("phone", "Telefone inválido.");
        valid = false;
    }
    if (!termsChecked) {
        setFieldError("terms", "É necessário aceitar os termos de uso.");
        valid = false;
    }

    if (!valid) return;

    const userId = getUserIdFromUrl();

    try {
        setFormStatus("Enviando...");

        const publicKeyResponse = await fetch("/static/js/crypt/public_key.pem");
        if (!publicKeyResponse.ok) {
            throw new Error("Não foi possível carregar a chave pública.");
        }
        const publicKeyPem = await publicKeyResponse.text();

        const emailHashBuffer = await _digestMessage(email);
        const emailHash = _arrayBufferToHexString(emailHashBuffer);

        const phoneDigits = phone.replace(/\D/g, "");

        const encryptedName = await dbEncryptString(name, publicKeyPem);
        const encryptedEmail = await dbEncryptString(email, publicKeyPem);
        const encryptedPhone = await dbEncryptString(phoneDigits, publicKeyPem);

        const response = await fetch(`/pages/form/${userId}/complete`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: encryptedName,
                email: encryptedEmail,
                email_hash: emailHash,
                phone: encryptedPhone,
            }),
        });

        const responseBody = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(responseBody.error || "Erro ao enviar formulário.");
        }

        setFormStatus("Dados enviados com sucesso!");
        window.location.href = responseBody.redirect || "/continue";
    } catch (error) {
        setFormStatus(error.message, true);
    }
}

document.getElementById("btnSubmit").addEventListener("click", handleSubmit);
document.getElementById("userForm").addEventListener("submit", (event) => {
    event.preventDefault();
    handleSubmit();
});
