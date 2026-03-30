const functions = require("@google-cloud/functions-framework");

functions.http("handler", (req, res) => {
  const response = {
    message: "Hello from Szymon!",
    team: "Zespół 1",
    timestamp: new Date().toISOString(),
  };
  res.json(response);
});
