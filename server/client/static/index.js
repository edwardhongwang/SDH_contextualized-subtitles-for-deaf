import { LineList } from "line-list";
import { PageRoot } from "page-root";
import { PageData } from "page-data";
import { PagePane } from "page-pane";
import { PageNav } from "page-nav";

const valid_events = new Set([
  "srt-page/enrich",
  "srt-pages/new"
])

const index = (user) => {
  // Pages
  customElements.define(
    "page-root", eventReceiver(
      PageRoot, PageRoot.eventHandlerKeys
    )
  );
  // Page
  customElements.define(
    "page-data", eventReceiver(
      PageData,
      PageData.eventHandlerKeys
    )
  );
  // Pane
  customElements.define(
    "page-pane", (
      inherit(PagePane, [
        "lines", "transcript_state", "id",
        "label", "source", "image", "header"
      ])
    )
  );
  // Subtitle lines
  customElements.define(
    "line-list", inherit(LineList, [
      "lines"
    ])
  )
  // Nav
  customElements.define(
    "page-nav", eventSender(PageNav)
  );
};


const eventSender = (element) => {
  return class extends element {
    sendCustomEvent(key, detail) {
      if (!valid_events.has(key)) {
        throw new Error(`Invalid Custom Event: "${key}"`);
      }
      const [bubbles, composed] = [true, true];
      this.shadowRoot.dispatchEvent(new CustomEvent(
        key, { detail, bubbles, composed }
      ));
    }
  }
}

const eventReceiver = (element, keys=[]) => {
  if (!keys.every(key => valid_events.has(key))) {
    throw new Error(`Invalid Custom Events`);
  }
  return class extends element {
    async connectedCallback() {
      await super.connectedCallback();
      keys.forEach(
        key => this.addEventListener(
          key, this.toEventHandler(key)
        )
      )
    }
  }
}


const inherit = (element, attrs) => {
  return class extends element {
    async connectedCallback() {
      const host = this.getRootNode().host;
      attrs.forEach(attr => {
        if (host.hasAttribute(attr)) {
          this.setAttribute(
            attr, host.getAttribute(attr)
          );
        };
      });
      await super.connectedCallback();
    }
  }
}


export { index }
