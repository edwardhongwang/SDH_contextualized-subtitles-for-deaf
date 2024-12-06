import StyleGlobal from "style-global" with { type: "css" };
import StylePageNav from "style-page-nav" with { type: "css" };

class PageNav extends HTMLElement {

  static observedAttributes = ["actions"];

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
    [
      [
        this.shadowRoot.getElementById("main"), () => {
          const host = this.getRootNode().host;
          this.sendCustomEvent("srt-page/enrich", {
            id: host.getAttribute("id")
          })
        }
      ],
      [
        this.shadowRoot.getElementById("new"), () => {
          const host = this.getRootNode().host;
          this.sendCustomEvent("srt-pages/new", { 
            id: host.getAttribute("id")
          })
        }
      ]
    ].map(
      ([el, action]) => el.addEventListener("click", action)
    )
    this.showButtonSet(this.getAttribute("actions"));
  }

  showButtonSet(actions) {
    const button_set = new Set(actions.split(" "));
    const buttons = this.shadowRoot.querySelectorAll("button");
    [...buttons].forEach((button) => {
      button.className= button_set.has(button.id) ? "" : "hide"
    })
  }

  attributeChangedCallback(key, _, value) {
    if (key == "actions") {
      this.showButtonSet(value);
    }
  }

}

export { PageNav };
