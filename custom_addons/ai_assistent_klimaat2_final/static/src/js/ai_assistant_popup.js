odoo.define('ai_assistant_klimaat2.popup', function(require) {
    'use strict';
    const { Dialog } = require('@web/core/dialog/dialog');
    const { registry } = require('@web/core/registry');
    const { useService } = require('@web/core/utils/hooks');

    class AIPopup {
        setup() {
            this.action = useService('action');
        }
        async start() {
            const controller = await this.action.getCurrentController();
            const model = controller.modelName;
            const recordId = controller.renderer.state.res_id;
            const content = document.createElement('div');
            const textarea = document.createElement('textarea');
            textarea.style.width = '100%';
            textarea.rows = 4;
            content.appendChild(textarea);

            const dialog = new Dialog(null, {
                title: 'Vraag AI Assistent',
                $content: content,
                buttons: [
                    { text: 'Verstuur', classes: 'btn-primary', close: true, click: async () => {
                        const prompt = textarea.value;
                        const res = await this.rpc('/ai_assistant/prompt', { prompt, model, res_id: recordId });
                        if (res.error) {
                            alert(res.error);
                        } else {
                            alert(res.antwoord);
                        }
                    }},
                    { text: 'Annuleer', close: true }
                ]
            });
            dialog.open();
        }
    }

    registry.category('actions').add('ai_assistant.popup', AIPopup);
});
