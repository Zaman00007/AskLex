import express from 'express';
import fs from 'fs';
import csv from 'csv-parser';
import { createObjectCsvWriter } from 'csv-writer';
import cors from 'cors';
import bodyParser from 'body-parser';

const app = express();
const PORT = 5000;
const CSV_FILE = './users.csv';

app.use(cors());
app.use(bodyParser.json());

if (!fs.existsSync(CSV_FILE)) {
  fs.writeFileSync(CSV_FILE, 'fullName,email,password\n');
}

const readUsers = () => {
  return new Promise((resolve, reject) => {
    const users = [];
    fs.createReadStream(CSV_FILE)
      .pipe(csv())
      .on('data', (data) => users.push(data))
      .on('end', () => resolve(users))
      .on('error', reject);
  });
};

const addUser = async (user) => {
  const csvWriter = createObjectCsvWriter({
    path: CSV_FILE,
    header: [
      { id: 'fullName', title: 'fullName' },
      { id: 'email', title: 'email' },
      { id: 'password', title: 'password' },
    ],
    append: true,
  });
  await csvWriter.writeRecords([user]);
};

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

// 🔐 Login endpoint
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  const users = await readUsers();

  const user = users.find((u) => u.email === email && u.password === password);
  if (!user)
    return res.status(401).json({ message: 'Invalid credentials' });

  res.json({ message: 'Login successful', fullName: user.fullName });
});

app.listen(PORT, () =>
  console.log(`✅ Server running at http://localhost:${PORT}`)
);
