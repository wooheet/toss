import React from "react";
import ReactDOM from "react-dom";
import App from "./Components/App";

import { Provider } from "mobx-react";
import Store from "./Stores/Store";

const store = new Store();

const RenderComponent = () => (
  <Provider yourstore={store}>
    <App />
  </Provider>
);

ReactDOM.render(
  <RenderComponent/>,
  document.getElementById("root")
);