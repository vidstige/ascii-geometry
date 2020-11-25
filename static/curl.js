function main() {
  const terminal = document.getElementById('terminal__prompt');

  var decoder = new TextDecoder();
  const consume = responseReader => {
    return responseReader.read().then(result => {
        if (result.done) { return; }
        const chunk = decoder.decode(result.value || new Uint8Array, {stream: !result.done});
        const index = chunk.lastIndexOf('\033[2J\033[1;1H')
        if (index >= 0) {
          terminal.innerText = chunk.substring(index + '\033[2J\033[1;1H'.length);
        } else {
          terminal.innerText += chunk;
        }
        return consume(responseReader);
    });
  }

  var url = '/torus?user-agent=curl?fps=10';
  fetch(url).then(response => {
      return consume(response.body.getReader());
  })
  .catch(console.error);

}
document.addEventListener("DOMContentLoaded", main);