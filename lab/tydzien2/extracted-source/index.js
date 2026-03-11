const functions = require('@google-cloud/functions-framework');

functions.http('helloHttp', (req, res) => {
  const response = {
    message: 'Hello from {Lukasz}!',
    team: 'Zespół {N}',
    timestamp: new Date().toISOString()
  };
  res.json(response);
});