import express from 'express';
import fs from 'fs';
import csv from 'csv-parser';
import { createObjectCsvWriter } from 'csv-writer';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
const PORT = 5000;
const USERS_FILE = './users.csv';
const REPORTS_FILE = './reports.csv';

app.use(cors());
app.use(bodyParser.json());

if (!fs.existsSync(USERS_FILE)) {
  fs.writeFileSync(USERS_FILE, 'fullName,email,password\n');
}

if (!fs.existsSync(REPORTS_FILE)) {
  fs.writeFileSync(REPORTS_FILE, 'email,crimeType,incident,culpritName,date,time\n');
}

const readUsers = () => {
  return new Promise((resolve, reject) => {
    const users = [];
    fs.createReadStream(USERS_FILE)
      .pipe(csv())
      .on('data', (data) => users.push(data))
      .on('end', () => resolve(users))
      .on('error', reject);
  });
};

const addUser = async (user) => {
  const csvWriter = createObjectCsvWriter({
    path: USERS_FILE,
    header: [
      { id: 'fullName', title: 'fullName' },
      { id: 'email', title: 'email' },
      { id: 'password', title: 'password' },
    ],
    append: true,
  });
  await csvWriter.writeRecords([user]);
};

// 🧩 Registration endpoint
app.post('/register', async (req, res) => {
  const { fullName, email, password } = req.body;
  if (!fullName || !email || !password)
    return res.status(400).json({ message: 'All fields required' });

  const users = await readUsers();
  const exists = users.find((u) => u.email === email);
  if (exists)
    return res.status(400).json({ message: 'Email already registered' });

  await addUser({ fullName, email, password });
  res.json({ message: 'Registration successful' });
});

app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const users = await readUsers();

  const user = users.find((u) => u.email === email && u.password === password);
  if (!user)
    return res.status(401).json({ message: 'Invalid credentials' });

  res.json({ message: 'Login successful', fullName: user.fullName, email });
});

app.post('/report', async (req, res) => {
  const { email, crimeType, incident, culpritName, date, time } = req.body;

  if (!email || !crimeType || !incident || !culpritName || !date || !time) {
    return res.status(400).json({ message: 'All fields are required' });
  }

  try {
    const csvWriter = createObjectCsvWriter({
      path: REPORTS_FILE,
      header: [
        { id: 'email', title: 'email' },
        { id: 'crimeType', title: 'crimeType' },
        { id: 'incident', title: 'incident' },
        { id: 'culpritName', title: 'culpritName' },
        { id: 'date', title: 'date' },
        { id: 'time', title: 'time' },
      ],
      append: true,
    });

    await csvWriter.writeRecords([{ email, crimeType, incident, culpritName, date, time }]);
    res.json({ message: 'Report saved successfully' });
  } catch (error) {
    console.error('Error writing report:', error);
    res.status(500).json({ message: 'Failed to save report' });
  }
});

app.get('/api/reports', (req, res) => {
  const email = req.query.email;
  if (!email) return res.status(400).json({ error: 'Missing email query' });
  const results = [];
  fs.createReadStream(REPORTS_FILE)
    .pipe(csv())
    .on('data', (data) => {
      if (data.email === email) results.push(data);
    })
    .on('end', () => res.json(results))
    .on('error', (err) => {
      console.error(err);
      res.status(500).json({ error: 'Error reading CSV file' });
    });
});

app.post('/api/close-report', (req, res) => {
  const report = req.body;
  const rows = [];

  fs.createReadStream(REPORTS_FILE)
    .pipe(csv())
    .on('data', (data) => rows.push(data))
    .on('end', () => {
      const filtered = rows.filter(
        (r) =>
          !(
            r.email === report.email &&
            r.crimeType === report.crimeType &&
            r.incident === report.incident &&
            r.culpritName === report.culpritName &&
            r.date === report.date &&
            r.time === report.time
          )
      );

      const csvWriter = createObjectCsvWriter({
        path: REPORTS_FILE,
        header: [
          { id: 'email', title: 'email' },
          { id: 'crimeType', title: 'crimeType' },
          { id: 'incident', title: 'incident' },
          { id: 'culpritName', title: 'culpritName' },
          { id: 'date', title: 'date' },
          { id: 'time', title: 'time' },
        ],
      });

      csvWriter
        .writeRecords(filtered)
        .then(() => res.json({ message: 'Report closed successfully!' }))
        .catch((err) => {
          console.error(err);
          res.status(500).json({ error: 'Error updating CSV file' });
        });
    })
    .on('error', (err) => {
      console.error(err);
      res.status(500).json({ error: 'Error reading CSV file' });
    });
});

app.listen(PORT, () =>
  console.log(`✅ Server running at http://localhost:${PORT}`)
);
