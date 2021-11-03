import React from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Game from "./components/Game/Game";
import Home from "./components/Home/Home";

function App() {
  return (
    <Router>
      <Switch>
        <Route exact path="/" component={Home} />
        <Route exact path="/:roomId" component={Game} />
      </Switch>
    </Router>
  );
}

export default App;