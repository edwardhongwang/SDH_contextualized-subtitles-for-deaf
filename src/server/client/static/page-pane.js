import StyleGlobal from "style-global" with { type: "css" };
import StylePagePane from "style-page-pane" with { type: "css" };

class PagePane extends HTMLElement {

  static observedAttributes = ["lines"];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePagePane
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-pane-view");
    const copy = template.content.cloneNode(true);
    this.renderLineList(copy);
    this.shadowRoot.appendChild(copy);
  }

  renderLineList(target) {
    const lines = this.getAttribute("lines");
    const line_list_el = target.querySelector("line-list");
    if (line_list_el) {
      line_list_el.setAttribute("lines", lines);
    }
  }

  attributeChangedCallback(key, _, value) {
    if (key == "lines") {
      this.renderLineList(this.shadowRoot);
    }
  }

}

export { PagePane };
