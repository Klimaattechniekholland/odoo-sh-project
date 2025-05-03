odoo.define('ai_assistant_klimaat2.popup', function (require) {
    const { Component, xml } = owl;
    const { patch } = require('web.utils');
    const { WebClient } = require('web.WebClient');
    const { Dialog } = require('web.Dialog');

    patch(WebClient.prototype, 'ai_assistant_popup_button', {
        start() {
            this._super(...arguments);
            const button = document.createElement("button");
            button.textContent = "🧠 AI Assistant";
            button.className = "btn btn-primary";
            button.style.position = "fixed";
            button.style.bottom = "20px";
            button.style.right = "20px";
            button.onclick = () => {
                new Dialog(this, {
                    title: "AI Assistent",
                    size: "large",
                    buttons: [],
                    $content: $(\`
                        <div>
                            <textarea id="ai_prompt" style="width:100%;height:100px;"></textarea>
                            <select id="ai_model">
                                <option value="gpt">GPT-4</option>
                                <option value="gemini">Gemini</option>
                            </select>
                            <button class="btn btn-info" onclick="aiSend()">Verstuur</button>
                            <pre id="ai_result"></pre>
                        </div>
                    \`)
                }).open();
            };
            document.body.appendChild(button);
        },
    });

    window.aiSend = async function () {
        const prompt = document.getElementById("ai_prompt").value;
        const model = document.getElementById("ai_model").value;
        const result = await fetch("/ai_assistant/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ prompt, model }),
        }).then(r => r.json());
        document.getElementById("ai_result").textContent = result.response || result.error;
    };
});
