document.getElementById('start').addEventListener('click', () => {
  chrome.storage.local.set({tracking: true});
  alert('Time tracking started!');
});
