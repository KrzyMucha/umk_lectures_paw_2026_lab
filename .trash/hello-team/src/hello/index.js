const functions = require('@google-cloud/functions-framework');

functions.http('handler', (req, res) => {
  const response = {
    message: 'Hello from Szymon Orzechowski!',
    team: 'Zespół R',
    timestamp: new Date().toISOString()
  };
  res.json(response);
});
