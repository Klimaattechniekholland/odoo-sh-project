odoo.define('ai_assistant_klimaat2.popup', function (require) {
    const { showTempDialog } = require('@web/core/dialog/dialog_service');
    const { registry } = require('@web/core/registry');
    const actionService = require('@web/webclient/actions/action_service');

    registry.category("actions").add("ai_assistant_popup", async function(env, action) {
        showTempDialog(env, {
            title: "AI Developer Assistant",
            body: "Hier komt de AI popup met GPT/Gemini integratie.",
        });
    });
});