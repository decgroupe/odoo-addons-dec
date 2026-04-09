// Copyright (C) DEC SARL, Inc - All Rights Reserved.
// Written by Yann Papouin <ypa at decgroupe.com>, Apr 2026

/* global window, document, console, FileReader */

import {
    Component,
    onMounted,
    onPatched,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import {loadCSS, loadJS} from "@web/core/assets";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {rpc} from "@web/core/network/rpc";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

const BUNDLE_BASE = "/web_widget_markdown/static/src/lib/draftly.bundle";

export class MarkdownField extends Component {
    static template = "web_widget_markdown.MarkdownField";
    static props = {
        ...standardFieldProps,
        readonly: {type: Boolean, optional: true},
    };

    setup() {
        this.orm = useService("orm");
        this.state = useState({renderMode: "live", indentWithTab: true});
        this.editorRef = useRef("editor");
        this.previewRef = useRef("preview");
        this.htmlOutputRef = useRef("htmlOutput");
        this.cssOutputRef = useRef("cssOutput");
        this.imageInputRef = useRef("imageInput");
        this._editorView = null;
        // Tracks which mode the current editor was created with
        this._editorMode = null;
        // Guard: prevents syncing back into the editor after record.update
        this._isEditorUpdate = false;
        onWillStart(async () => {
            await Promise.all([
                loadJS(`${BUNDLE_BASE}.js`),
                loadCSS(`${BUNDLE_BASE}.css`),
            ]);
        });
        onMounted(() => this._syncDom());
        onPatched(() => this._syncDom());
        onWillUnmount(() => this._destroyEditor());
    }

    get modes() {
        return [
            {
                key: "live",
                label: _t("Live"),
                title: _t("WYSIWYG editor"),
                icon: "fa-magic",
            },
            {
                key: "view",
                label: _t("View"),
                title: _t("Rendered HTML preview"),
                icon: "fa-eye",
            },
            {
                key: "code",
                label: _t("Code"),
                title: _t("Raw Markdown source"),
                icon: "fa-code",
            },
            {
                key: "output",
                label: _t("Output"),
                title: _t("Raw HTML and CSS source"),
                icon: "fa-file-text",
            },
        ];
    }

    get editActions() {
        return [
            {key: "heading", title: _t("Heading"), icon: "fa-header"},
            {key: "bold", title: _t("Bold (Ctrl+B)"), icon: "fa-bold"},
            {key: "italic", title: _t("Italic (Ctrl+I)"), icon: "fa-italic"},
            {
                key: "strikethrough",
                title: _t("Strikethrough (Ctrl+Shift+S)"),
                icon: "fa-strikethrough",
            },
            {
                key: "highlight",
                title: _t("Highlight (Ctrl+Shift+H)"),
                icon: "fa-paint-brush",
            },
            {key: "subscript", title: _t("Subscript (Ctrl+,)"), icon: "fa-subscript"},
            {
                key: "superscript",
                title: _t("Superscript (Ctrl+.)"),
                icon: "fa-superscript",
            },
            {key: "quote", title: _t("Quote"), icon: "fa-quote-left"},
            {key: "code", title: _t("Code (Ctrl+E / Ctrl+Shift+E)"), icon: "fa-code"},
            {key: "link", title: _t("Link (Ctrl+K)"), icon: "fa-link"},
            {
                key: "numbered-list",
                title: _t("Numbered list (Ctrl+Shift+7)"),
                icon: "fa-list-ol",
            },
            {
                key: "unordered-list",
                title: _t("Unordered list (Ctrl+Shift+8)"),
                icon: "fa-list-ul",
            },
            {
                key: "task-list",
                title: _t("Task list (Ctrl+Shift+9)"),
                icon: "fa-check-square-o",
            },
        ];
    }

    get value() {
        return this.props.record.data[this.props.name] || "";
    }

    onModeChange(ev) {
        this.state.renderMode = ev.currentTarget.value;
    }

    onToggleIndentWithTab() {
        this.state.indentWithTab = !this.state.indentWithTab;
        // Destroy so _syncDom/onPatched recreates the editor with the new setting
        this._destroyEditor();
    }

    onInsertImage() {
        this.imageInputRef.el?.click();
    }

    async onImageFileSelected(ev) {
        const file = ev.target.files[0];
        // Reset so the same file can be re-selected later
        ev.target.value = "";
        if (!file || !this._editorView) {
            return;
        }
        await this._uploadPastedImage(file, this._editorView);
    }

    onPrint() {
        document.body.classList.add("o_printing_markdown");
        window.addEventListener(
            "afterprint",
            () => {
                document.body.classList.remove("o_printing_markdown");
            },
            {once: true}
        );
        window.print();
    }

    onEditAction(ev) {
        const key = ev.currentTarget.dataset.action;
        const view = this._editorView;
        if (!view) {
            return;
        }
        this._applyMarkdown(view, key);
        view.focus();
    }

    _applyMarkdown(view, action) {
        const state = view.state;
        const {from, to} = state.selection.main;
        const selected = state.sliceDoc(from, to);
        // Wrap selection (or cursor) with before/after delimiters
        const wrap = (before, after) => {
            const _after = after === undefined ? before : after;
            view.dispatch({
                changes: [
                    {from, insert: before},
                    {from: to, insert: _after},
                ],
                selection: {anchor: from + before.length, head: to + before.length},
            });
        };
        // Insert prefix at the start of the line containing the cursor
        const prefixLine = (prefix) => {
            const line = state.doc.lineAt(from);
            view.dispatch({
                changes: {from: line.from, insert: prefix},
                selection: {anchor: from + prefix.length, head: to + prefix.length},
            });
        };
        switch (action) {
            case "heading":
                prefixLine("## ");
                break;
            case "bold":
                wrap("**");
                break;
            case "italic":
                wrap("_");
                break;
            case "quote":
                prefixLine("> ");
                break;
            case "code":
                if (selected.includes("\n")) {
                    wrap("```", "```");
                } else {
                    wrap("`");
                }
                break;
            case "link":
                view.dispatch({
                    changes: {from, to, insert: `[${selected}](url)`},
                    // Select the placeholder "url" so user can type immediately
                    selection: {
                        anchor: from + selected.length + 3,
                        head: from + selected.length + 6,
                    },
                });
                break;
            case "numbered-list":
                prefixLine("1. ");
                break;
            case "unordered-list":
                prefixLine("- ");
                break;
            case "task-list":
                prefixLine("- [ ] ");
                break;
            case "strikethrough":
                wrap("~~");
                break;
            case "highlight":
                wrap("==");
                break;
            case "subscript":
                wrap("~");
                break;
            case "superscript":
                wrap("^");
                break;
        }
    }

    _destroyEditor() {
        if (this._editorView) {
            this._editorView.destroy();
            this._editorView = null;
            this._editorMode = null;
        }
    }

    async _uploadPastedImage(file, view) {
        // Read a pasted image File, upload it as an ir.attachment, and insert
        // the resulting markdown image syntax at the current cursor position.
        const dataUrl = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
        const base64 = dataUrl.split(",")[1];
        const record = this.props.record;
        const fileName = file.name || `pasted-image-${Date.now()}`;
        const attachment = await rpc("/web_editor/attachment/add_data", {
            name: fileName,
            data: base64,
            is_image: true,
            res_model: record.resModel,
            res_id: record.resId || 0,
        });
        if (attachment.error) {
            console.error(
                "[web_widget_markdown] image upload failed:",
                attachment.error
            );
            return;
        }
        let src = attachment.image_src;
        if (!attachment.public) {
            let accessToken = attachment.access_token;
            if (!accessToken) {
                [accessToken] = await this.orm.call(
                    "ir.attachment",
                    "generate_access_token",
                    [attachment.id]
                );
            }
            src += `?access_token=${encodeURIComponent(accessToken)}`;
        }
        const altText = fileName.replace(/\.[^.]+$/, "");
        const md = `![${altText}](${src})`;
        const {from, to} = view.state.selection.main;
        view.dispatch({
            changes: {from, to, insert: md},
            selection: {anchor: from + md.length},
        });
    }

    _initEditor() {
        const el = this.editorRef.el;
        if (!el || this._editorView) {
            return;
        }
        const {EditorState, EditorView, draftly, allPlugins, codeExtensions} =
            window.Draftly;
        const mode = this.state.renderMode;
        const isCode = mode === "code";
        this._editorView = new EditorView({
            state: EditorState.create({
                doc: this.value,
                extensions: [
                    draftly({
                        theme: "auto",
                        plugins: allPlugins,
                        lineWrapping: true,
                        history: true,
                        indentWithTab: this.state.indentWithTab,
                        // Code mode disables the WYSIWYG decoration layer
                        disableViewPlugin: isCode,
                        highlightActiveLine: isCode,
                    }),
                    // Code mode: add line numbers and full token-level syntax colours
                    ...(isCode ? codeExtensions : []),
                    EditorView.domEventHandlers({
                        paste: (event, view) => {
                            const items = Array.from(event.clipboardData?.items || []);
                            const imageItems = items.filter((item) =>
                                item.type.startsWith("image/")
                            );
                            if (!imageItems.length) {
                                // Let draftly/codemirror handle non-image paste
                                return false;
                            }
                            event.preventDefault();
                            for (const item of imageItems) {
                                const file = item.getAsFile();
                                if (file) {
                                    this._uploadPastedImage(file, view);
                                }
                            }
                            return true;
                        },
                    }),
                    EditorView.updateListener.of((update) => {
                        if (!update.docChanged) {
                            return;
                        }
                        this._isEditorUpdate = true;
                        this.props.record.update({
                            [this.props.name]: update.state.doc.toString(),
                        });
                    }),
                ],
            }),
            parent: el,
        });
        this._editorMode = mode;
    }

    async _renderPreview() {
        const el = this.previewRef.el;
        if (!el) {
            return;
        }
        const {preview, generateCSS, allPlugins} = window.Draftly;
        const WRAPPER = "o_field_markdown_preview";
        const [html, css] = await Promise.all([
            preview(this.value, {
                theme: "auto",
                plugins: allPlugins,
                sanitize: true,
                wrapperClass: WRAPPER,
            }),
            Promise.resolve(
                generateCSS({
                    theme: "auto",
                    plugins: allPlugins,
                    wrapperClass: WRAPPER,
                    includeBase: true,
                })
            ),
        ]);
        // Guard: element may have been removed from the DOM while awaiting
        if (!el.isConnected) {
            return;
        }
        el.innerHTML = `<style>${css}</style>${html}`;
    }

    async _renderOutput() {
        const htmlEl = this.htmlOutputRef.el;
        const cssEl = this.cssOutputRef.el;
        if (!htmlEl || !cssEl) {
            return;
        }
        const {preview, generateCSS, allPlugins} = window.Draftly;
        const [html, css] = await Promise.all([
            preview(this.value, {
                theme: "auto",
                plugins: allPlugins,
                sanitize: true,
            }),
            Promise.resolve(
                generateCSS({
                    theme: "auto",
                    plugins: allPlugins,
                    includeBase: true,
                })
            ),
        ]);
        if (htmlEl.isConnected) {
            htmlEl.textContent = html;
        }
        if (cssEl.isConnected) {
            cssEl.textContent = css;
        }
    }

    _syncDom() {
        const mode = this.props.readonly ? "view" : this.state.renderMode;
        if (mode === "view") {
            this._destroyEditor();
            this._renderPreview();
            return;
        }
        if (mode === "output") {
            this._destroyEditor();
            this._renderOutput();
            return;
        }
        // Modes "live" and "code" require an editor
        // destroy and recreate when switching between them (different draftly options)
        if (this._editorView && this._editorMode !== mode) {
            this._destroyEditor();
        }
        if (!this._editorView) {
            this._initEditor();
        } else if (this._isEditorUpdate) {
            // This patch was triggered by the editor itself: skip value sync
            this._isEditorUpdate = false;
        } else {
            // Sync external value changes (e.g. server reload, discard)
            const current = this._editorView.state.doc.toString();
            const incoming = this.value;
            if (current !== incoming) {
                this._editorView.dispatch({
                    changes: {from: 0, to: current.length, insert: incoming},
                });
            }
        }
    }
}

export const markdownField = {
    component: MarkdownField,
    displayName: _t("Markdown"),
    supportedTypes: ["text"],
    extractProps: () => ({}),
};

registry.category("fields").add("markdown", markdownField);
