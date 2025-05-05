odoo.define('ai_integration.ai_widget', function (require) {
    "use strict";
    const publicWidget = require('web.public.widget');
    const rpc = require('web.rpc');

    publicWidget.registry.AIWidget = publicWidget.Widget.extend({
        selector: '.o_ai_widget',
        events: {
            'click .o_ai_send': '_onClickSend',
        },
        start: function () {
            this.$promptInput = this.$el.find('.o_ai_prompt_input');
            this.$responseArea = this.$el.find('.o_ai_response');
            return this._super.apply(this, arguments);
        },
        _onClickSend: function () {
            const prompt = this.$promptInput.val().trim();
            if (!prompt) {
                this.$responseArea.text('Voer eerst een prompt in.');
                return;
            }
            this.$responseArea.text('Bezig met laden...');
            rpc.rpc({
                route: '/ai_integration/ask',
                params: { prompt: prompt },
            }).then(response => {
                this.$responseArea.text(response);
            }).catch(error => {
                console.error(error);
                this.$responseArea.text('Er is een fout opgetreden bij de AI-aanvraag.');
            });
        },
    });
});