// --- Máscaras ---

function maskName(value) {
    return value.replace(/[^A-Za-zÀ-ÖØ-öø-ÿ\s]/g, "");
}

function maskCPF(value) {
    const digits = value.replace(/\D/g, "").slice(0, 11);
    if (digits.length > 9) {
        return digits.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, "$1.$2.$3-$4");
    }
    if (digits.length > 6) {
        return digits.replace(/(\d{3})(\d{3})(\d{1,3})/, "$1.$2.$3");
    }
    if (digits.length > 3) {
        return digits.replace(/(\d{3})(\d{1,3})/, "$1.$2");
    }
    return digits;
}

// --- Validação ---

function isAdult(age) {
    const value = parseInt(age, 10);
    return Number.isInteger(value) && value >= 18;
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidCPF(cpf) {
    const digits = cpf.replace(/\D/g, "");
    if (digits.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(digits)) return false;

    const calcCheckDigit = (base) => {
        let sum = 0;
        let weight = base.length + 1;
        for (const digit of base) {
            sum += parseInt(digit, 10) * weight;
            weight -= 1;
        }
        const remainder = sum % 11;
        return remainder < 2 ? 0 : 11 - remainder;
    };

    const base9 = digits.slice(0, 9);
    const firstCheck = calcCheckDigit(base9);
    const secondCheck = calcCheckDigit(base9 + String(firstCheck));

    return digits === base9 + String(firstCheck) + String(secondCheck);
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

document.getElementById("cpf").addEventListener("input", (event) => {
    event.target.value = maskCPF(event.target.value);
});

// --- Envio ---

async function handleSubmit() {
    setFormStatus("");
    ["name", "age", "email", "cpf", "terms"].forEach((field) => setFieldError(field, ""));

    const name = document.getElementById("name").value.trim();
    const age = document.getElementById("age").value;
    const email = document.getElementById("email").value.trim();
    const cpf = document.getElementById("cpf").value;
    const termsChecked = document.getElementById("terms").checked;

    let valid = true;

    if (!name) {
        setFieldError("name", "Informe seu nome.");
        valid = false;
    }
    if (!isAdult(age)) {
        setFieldError("age", "Você deve ter 18 anos ou mais.");
        valid = false;
    }
    if (!isValidEmail(email)) {
        setFieldError("email", "E-mail inválido.");
        valid = false;
    }
    if (!isValidCPF(cpf)) {
        setFieldError("cpf", "CPF inválido.");
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

        const cpfDigits = cpf.replace(/\D/g, "");

        const encryptedName = await dbEncryptString(name, publicKeyPem);
        const encryptedEmail = await dbEncryptString(email, publicKeyPem);
        const encryptedCpf = await dbEncryptString(cpfDigits, publicKeyPem);

        const response = await fetch(`/users/${userId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: encryptedName,
                email: encryptedEmail,
                email_hash: emailHash,
                cpf: encryptedCpf,
                status: "form",
            }),
        });

        if (!response.ok) {
            const errorBody = await response.json().catch(() => ({}));
            throw new Error(errorBody.error || "Erro ao enviar formulário.");
        }

        setFormStatus("Dados enviados com sucesso!");
    } catch (error) {
        setFormStatus(error.message, true);
    }
}

document.getElementById("btnSubmit").addEventListener("click", handleSubmit);
document.getElementById("userForm").addEventListener("submit", (event) => {
    event.preventDefault();
    handleSubmit();
});
