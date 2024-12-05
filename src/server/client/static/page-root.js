import StyleGlobal from "style-global" with { type: "css" };
import StylePageRoot from "style-page-root" with { type: "css" };

class PageRoot extends HTMLElement {

  static eventHandlerKeys = [
    "srt-lines/redraw"
  ];

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.shadowRoot.adoptedStyleSheets = [
      StyleGlobal, StylePageRoot
    ];
  }

  async connectedCallback() {
    await this.render();
  }

  async render() {
    this.shadowRoot.innerHTML = "";
    const template = document.getElementById("page-root-view");
    this.shadowRoot.appendChild(template.content.cloneNode(true));
  }

  toEventHandler(key) {
    if (key === "srt-lines/redraw") {
      return async ({ detail }) => {
        const panes = this.shadowRoot.querySelectorAll(
          "page-pane"
        );
        await Promise.all(
          [...panes].map(pane => {
            pane.setAttribute("lines", detail.lines.join(" "));
          })
        );
      }
    }
  }

}

export { PageRoot };
