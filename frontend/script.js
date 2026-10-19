/* ThreatMeter frontend: presentation only.
   The phishing prediction must come from the FastAPI backend, not browser rules. */
(function () {
  'use strict';

  // Change this only if your backend uses a different host, port, or route.
  const API_URL = 'http://127.0.0.1:8000/analyze';

  // Examples are specific to the selected analyzer. URL examples use reserved
  // .example domains and are illustrative only, not live websites.
  const examples = {
    sms: {
      prize: 'Congratulations! You have won ₹50,000. Claim your prize now. Send your OTP to verify your identity.',
      account: 'URGENT: Your bank account will be blocked today. Reply with your OTP and PIN to restore access.',
      work: 'Hi team, our project meeting is scheduled for tomorrow at 10 AM. Please bring your progress update. Thanks!'
    },
    email: {
      prize: 'Subject: You have been selected for a reward\n\nCongratulations! You have won a special cash reward. Pay a processing fee today to release your prize.',
      account: 'Subject: Urgent account verification required\n\nYour account will be suspended within 24 hours. Click the verification link and provide your password and one-time code to keep it active.',
      work: 'Subject: Project meeting tomorrow\n\nHi team, our project meeting is scheduled for tomorrow at 10 AM. Please bring your progress updates and the revised presentation. Thanks!'
    },
    url: {
      prize: 'https://claim-prize.example/redeem-now',
      account: 'https://secure-bank-login.example/verify-account',
      work: 'https://www.example.com/'
    }
  };

  const exampleButtonLabels = {
    sms: [
      { key: 'prize', label: 'Prize claim', icon: '#i-gift' },
      { key: 'account', label: 'OTP scam', icon: '#i-shield' },
      { key: 'work', label: 'Normal SMS', icon: '#i-mail' }
    ],
    email: [
      { key: 'prize', label: 'Reward email', icon: '#i-gift' },
      { key: 'account', label: 'Account alert', icon: '#i-shield' },
      { key: 'work', label: 'Work email', icon: '#i-mail' }
    ],
    url: [
      { key: 'prize', label: 'Prize URL', icon: '#i-gift' },
      { key: 'account', label: 'Login URL', icon: '#i-shield' },
      { key: 'work', label: 'Example URL', icon: '#i-code' }
    ]
  };
  
  const form = document.getElementById('analyzer-form');
  const input = document.getElementById('message');
  let selectedType = 'sms';
  const analysisTypeButtons = document.querySelectorAll('[data-analysis-type]');
  const results = document.getElementById('results');
  const analyzeButton = document.getElementById('analyze-button');
  const scanLine = document.getElementById('scan-line');
  const scanStatus = document.getElementById('scan-status');
  const error = document.getElementById('input-error');
  const menuToggle = document.getElementById('menu-toggle');
  const navigation = document.getElementById('navigation');
  const themeToggle = document.getElementById('theme-toggle');
  const themeToggleLabel = document.getElementById('theme-toggle-label');
  const themeToggleIcon = document.getElementById('theme-toggle-icon');

  function applyTheme(theme) {
    const isLight = theme === 'light';
    document.documentElement.dataset.theme = isLight ? 'light' : 'dark';
    if (themeToggle) {
      themeToggle.setAttribute('aria-pressed', String(isLight));
      themeToggle.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
      themeToggle.title = isLight ? 'Switch to dark mode' : 'Switch to light mode';
    }
    if (themeToggleLabel) themeToggleLabel.textContent = isLight ? 'Dark mode' : 'Light mode';
    if (themeToggleIcon) themeToggleIcon.setAttribute('href', isLight ? '#i-shield' : '#i-scan');
  }

  let savedTheme = 'dark';
  try {
    savedTheme = localStorage.getItem('threatmeter-theme') === 'light' ? 'light' : 'dark';
  } catch (_) {
    savedTheme = 'dark';
  }
  applyTheme(savedTheme);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const nextTheme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
      applyTheme(nextTheme);
      try {
        localStorage.setItem('threatmeter-theme', nextTheme);
      } catch (_) {
        // Theme still works for the current page if storage is unavailable.
      }
    });
  }

  if (!form || !input || !results || !analyzeButton) return;

  const originalButton = analyzeButton.innerHTML;

  function motionBehavior() {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
  }

  function updateCount() {
    const count = Array.from(input.value).length;
    document.getElementById('character-count').textContent =
      count + (count === 1 ? ' character' : ' characters');
    error.hidden = true;
    input.removeAttribute('aria-invalid');
    results.hidden = true;
  }

  function setBusy(busy) {
    analyzeButton.disabled = busy;
    input.readOnly = busy;
    if (busy) {
      form.setAttribute('aria-busy', 'true');
      scanLine.hidden = false;
      scanStatus.hidden = false;
      scanStatus.textContent = 'Sending message to the analysis service…';
      analyzeButton.innerHTML =
        '<span class="spinner" aria-hidden="true"></span><span>Analyzing message…</span>';
    } else {
      form.removeAttribute('aria-busy');
      scanLine.hidden = true;
      scanStatus.hidden = true;
      analyzeButton.innerHTML = originalButton;
    }
  }

  function reset() {
    setBusy(false);
    input.value = '';
    updateCount();
    input.focus();
  }

  function fillList(id, items) {
    const list = document.getElementById(id);
    list.replaceChildren();
    (Array.isArray(items) ? items : []).forEach(item => {
      const li = document.createElement('li');
      li.textContent = String(item);
      list.appendChild(li);
    });
  }

  function showResult(result) {
    const status = String(result.status || result.label || 'unknown').toLowerCase();
    const isPhishing = ['phishing', 'malicious', 'suspicious', 'high_risk'].includes(status);
    const isSafe = ['safe', 'legitimate', 'ham', 'not_phishing', 'low_risk'].includes(status);
    const normalizedStatus = isPhishing ? 'phishing' : isSafe ? 'safe' : 'unknown';

    
    
    // Select the correct threat probability for each mode.
    const probability = selectedType === 'sms'
      ? result.spam_probability
      : result.phishing_probability;



    const hasProbability =
      typeof probability === 'number' &&
      Number.isFinite(probability) &&
      probability >= 0 &&
      probability <= 1;

    const threatScore = hasProbability
      ? probability * 100
      : null;

    const scoreValue = document.getElementById('threat-score-value');
    const centerValue = document.getElementById('meter-center-value');
    const meterProgress = document.getElementById('meter-progress');
    const meter = document.getElementById('threat-meter');
    const scoreDescription = document.getElementById('threat-score-description');

    if (threatScore !== null) {
      const displayedScore = threatScore.toFixed(2);
      const circumference = 2 * Math.PI * 48;

      scoreValue.textContent = displayedScore;
      centerValue.textContent = displayedScore + '%';
      meterProgress.style.strokeDashoffset =
        String(circumference * (1 - threatScore / 100));

      meter.setAttribute(
        'aria-label',
        'Estimated threat probability: ' + displayedScore + ' percent'
      );

      scoreDescription.textContent = selectedType === 'sms'
  ? 'Estimated spam probability'
  : 'Estimated phishing probability';

    } else {
      scoreValue.textContent = 'N/A';
      centerValue.textContent = 'N/A';
      meterProgress.style.strokeDashoffset = String(2 * Math.PI * 48);
      meter.setAttribute('aria-label', 'Threat probability unavailable');
      scoreDescription.textContent = 'Probability not provided by the model';
    }

    const title = result.label || (isPhishing
      ? 'Potentially Phishing'
      : isSafe ? 'Likely Legitimate' : 'Unable to Determine');

    document.getElementById('result-title').textContent = title;
    document.getElementById('result-summary').textContent =
      result.summary || result.message ||
      (isPhishing
        ? 'The ML model classified this message as potentially phishing. Verify it independently before taking action.'
        : isSafe
          ? 'The ML model classified this message as likely legitimate. This does not guarantee that it is safe.'
          : 'The model did not return a clear classification. Verify the sender and request independently.');

    const confidence = result.confidence;
    const score = result.score;
    const meta = document.querySelector('#results .result-top small');
    if (meta) {
      const details = [];
      if (confidence !== undefined && confidence !== null && confidence !== '') {
        details.push('Confidence: ' + String(confidence));
      } else if (typeof score === 'number') {
        details.push('Model score: ' + score);
      }
      meta.textContent = details.length ? 'ML Model Analysis · ' + details.join(' · ') : 'ML Model Analysis';
    }

    document.getElementById('result-icon-use').setAttribute(
      'href', normalizedStatus === 'safe' ? '#i-shield' :
        normalizedStatus === 'phishing' ? '#i-warning' : '#i-info'
    );
    const indicators = result.indicators || result.reasons || [];
    const recommendations = result.recommendations || [
      'Verify the sender through a trusted, independent channel.',
      'Do not share passwords, one-time codes, or financial information in response to an unexpected message.'
    ];
    document.getElementById('indicator-heading').textContent =
      'Model Findings' + (indicators.length ? ' · ' + indicators.length : '');
    fillList('indicators', indicators.length ? indicators : [
      'The backend returned a classification without additional explanatory indicators.'
    ]);
    fillList('recommendations', recommendations);
    results.dataset.status = normalizedStatus;
    results.hidden = false;
    results.focus({ preventScroll: true });
    results.scrollIntoView({ behavior: motionBehavior(), block: 'center' });
  }
  
  function updateAnalysisType(type) {
    selectedType = type;

    analysisTypeButtons.forEach(button => {
      const isActive = button.dataset.analysisType === type;
      button.classList.toggle('active', isActive);
      button.setAttribute('aria-pressed', String(isActive));
    });

    const labels = {
      sms: {
        label: 'SMS message to analyze',
        placeholder: 'Paste your suspicious SMS or text message here...',
        button: 'Analyze SMS',
        examplesHeading: 'Try an SMS example:'
      },
      email: {
        label: 'Email to analyze',
        placeholder: 'Paste the email subject and body here...',
        button: 'Analyze Email',
        examplesHeading: 'Try an email example:'
      },
      // URL and image modes remain unavailable until their detectors are ready.
    };

    const config = labels[type];
    if (!config) return;

    document.querySelector('label[for="message"]').textContent = config.label;
    input.placeholder = config.placeholder;
    analyzeButton.querySelector('span').textContent = config.button;

    const examplesHeading = document.querySelector('.examples > span');
    if (examplesHeading) examplesHeading.textContent = config.examplesHeading;

    document.querySelectorAll('.example-btn[data-example]').forEach(button => {
      const item = (exampleButtonLabels[type] || []).find(
        example => example.key === button.dataset.example
      );
      if (!item) return;
      const icon = button.querySelector('use');
      if (icon) icon.setAttribute('href', item.icon);
      // Update only the visible label, preserving the icon.
      const visibleText = Array.from(button.childNodes).find(node =>
        node.nodeType === Node.TEXT_NODE && node.textContent.trim()
      );
      if (visibleText) {
        visibleText.textContent = ' ' + item.label;
      } else {
        button.appendChild(document.createTextNode(' ' + item.label));
      }
      button.setAttribute('aria-label', 'Fill example: ' + item.label);
    });

    results.hidden = true;
    error.hidden = true;
    input.removeAttribute('aria-invalid');
  }

  analysisTypeButtons.forEach(button => {
    button.addEventListener('click', () => {
      if (button.disabled || button.dataset.analysisType === 'url' ||
          button.dataset.analysisType === 'image') return;
      updateAnalysisType(button.dataset.analysisType);
    });
  });

  // Set the matching example labels on first load (SMS is the default mode).
  updateAnalysisType(selectedType);

  input.addEventListener('input', updateCount);
  document.getElementById('clear').addEventListener('click', reset);
  document.getElementById('analyze-another').addEventListener('click', () => {
    reset();
    input.scrollIntoView({ block: 'center', behavior: motionBehavior() });
  });

  document.querySelectorAll('[data-example]').forEach(button => {
    button.addEventListener('click', () => {
      setBusy(false);
      const modeExamples = examples[selectedType] || {};
      input.value = modeExamples[button.dataset.example] || '';
      updateCount();
      input.focus();
    });
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (analyzeButton.disabled) return;

    const message = input.value.trim();
    if (!message) {
      error.textContent = 'Please paste a message before analyzing.';
      error.hidden = false;
      input.setAttribute('aria-invalid', 'true');
      input.focus();
      return;
    }

    if (selectedType !== 'sms' && selectedType !== 'email') {
      error.textContent = 'This analyzer is coming soon. Please choose SMS or Email.';
      error.hidden = false;
      return;
    }

    results.hidden = true;
    error.hidden = true;
    setBusy(true);

    try {
      const endpointMap = {
        sms: 'http://127.0.0.1:8000/analyze',
        email: 'http://127.0.0.1:8000/analyze-email'
      };

      const requestBodyMap = {
        sms: { message: message },
        email: { text: message }
      };

      const response = await fetch(endpointMap[selectedType], {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBodyMap[selectedType])
      });

      let data;
      try {
        data = await response.json();
      } catch (_) {
        throw new Error('The backend returned an unreadable response.');
      }

      if (!response.ok) {
        throw new Error(data.detail || data.error || ('Analysis failed (HTTP ' + response.status + ').'));
      }
      setBusy(false);
      showResult(data);
    } catch (err) {
      setBusy(false);
      results.hidden = true;
      error.textContent = err instanceof TypeError
        ? 'Cannot reach the analysis service. Make sure the FastAPI backend is running and its CORS settings allow this frontend.'
        : (err.message || 'Something went wrong while analyzing this message.');
      error.hidden = false;
      input.setAttribute('aria-invalid', 'true');
    }
  });

  menuToggle.addEventListener('click', () => {
    const open = navigation.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', String(open));
    menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });

  document.querySelectorAll('a[href^="#"]').forEach(link => link.addEventListener('click', () => {
    navigation.classList.remove('open');
    menuToggle.setAttribute('aria-expanded', 'false');
    menuToggle.setAttribute('aria-label', 'Open navigation');
  }));

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      navigation.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
      menuToggle.setAttribute('aria-label', 'Open navigation');
    }
  });

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          navigation.querySelectorAll('a').forEach(link =>
            link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id)
          );
        }
      });
    }, { rootMargin: '-15% 0px -55% 0px' });
    ['home', 'analyze', 'how-it-works', 'about'].forEach(id => {
      const section = document.getElementById(id);
      if (section) observer.observe(section);
    });
  }
})();
