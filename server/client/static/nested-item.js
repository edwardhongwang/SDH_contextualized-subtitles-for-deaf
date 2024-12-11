import StyleGlobal from "style-global" with { type: "css" };
import StyleNestedItem from "style-nested-item" with { type: "css" };

class NestedItem extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StyleNestedItem
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const button_el = document.createElement("button");
    const span_0 = document.createElement("span");
    const span_1 = document.createElement("span");
    const clip_id = this.getAttribute("clip_id");
    button_el.addEventListener("click", () => {
      this.sendCustomEvent("srt-pages/new", { 
        listing: this.getAttribute("listing"),
        clip_id: this.getAttribute("clip_id")
      });
    });
    span_0.innerHTML = 'clip';
    span_1.innerHTML = clip_id;
    button_el.appendChild(span_0);
    button_el.appendChild(span_1);
    this.shadowRoot.appendChild(button_el);
  }
};

export { NestedItem };
