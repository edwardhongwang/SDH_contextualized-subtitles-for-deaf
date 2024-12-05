import { LineList } from "line-list";
import { PageRoot } from "page-root";
import { PagePane } from "page-pane";
import { PageNav } from "page-nav";

const valid_events = new Set([
  "srt-lines/redraw"
])

const index = (user) => {
  // Subtitle lines
  customElements.define(
    "line-list", LineList
  )
  // Nav
  customElements.define(
    "page-nav", eventSender(PageNav)
  );
  // Page 
  customElements.define(
    "page-root", eventReceiver(
      PageRoot, PageRoot.eventHandlerKeys
    )
  );
  // Pane
  customElements.define(
    "page-pane", eventReceiver(
      PagePane, PagePane.eventHandlerKeys
    )
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


const inherit = (element, attrs=["self"]) => {
  return class extends element {
    render() {
      const host = this.getRootNode().host;
      attrs.forEach(attr => {
        if (!host.hasAttribute(attr)) return;
        this.setAttribute(attr, host.getAttribute(attr));
      });
      super.render();
    }
  }
}


export { index }
