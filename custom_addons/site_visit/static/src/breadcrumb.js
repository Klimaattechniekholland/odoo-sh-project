/** @odoo-module **/

odoo.define('site_visit.breadcrumb', ['@web/core/registry'], function (require) {
    'use strict';

    console.log("💡 Breadcrumb JS loaded");

    const { registry } = require("@web/core/registry");
    const actionService = registry.category("services").get("action");

    document.addEventListener("click", function (ev) {
        console.log("🟡 Click detected:", ev.target);

        const target = ev.target instanceof Element ? ev.target : ev.target.parentElement;
        const link = target?.closest('a[data-breadcrumb]');

        console.log("🔎 Found link:", link);

        if (!link) {
            console.warn("⚠️ No breadcrumb link with data-breadcrumb found.");
            return;
        }

        ev.preventDefault();

        let data;
        try {
            data = JSON.parse(link.dataset.breadcrumb);
        } catch (err) {
            console.error("❌ Failed to parse breadcrumb data:", err);
            return;
        }

        const { model, id } = data || {};

        console.log("📦 Parsed breadcrumb:", { model, id });

        if (!model || !id) {
            console.warn("⚠️ Missing model or ID. Skipping action.");
            return;
        }

        actionService.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: id,
            view_mode: "form",
            target: "current",
        });

        console.log("🚀 Action triggered:", model, id);
    });
});
