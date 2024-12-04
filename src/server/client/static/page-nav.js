import StyleGlobal from "style-global" with { type: "css" };
import StylePageNav from "style-page-nav" with { type: "css" };

class PageNav extends HTMLElement {

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageNav
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-nav-view");
    this.shadowRoot.appendChild(template.content.cloneNode(true));
    const button = this.shadowRoot.querySelector("button");
    button.addEventListener("click", () => {
      const lines = [...new Array(3).keys()].map(() => {
        return Math.ceil(Math.random()*10);
      });
      this.sendCustomEvent("srt-lines/redraw", { lines })
    })
  }

}

export { PageNav };
