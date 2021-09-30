function get(url) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", url, false);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(null);
  var info = JSON.parse(xhr.response);
  return info;
}

function post(url, data) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", url, true);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify(data));
}

function get_checked_party() {
  selectors = document.getElementsByClassName("party-selector");
  for (selector of selectors) {
    if (selector.checked) {
      console.log("This selector is checked:", selector);
      return selector.getAttribute("value");
    }
  }
}

function get_current_values() {
  let party = get_checked_party();
  let politician_id = document
    .getElementById("politician_id")
    .getAttribute("value");
  let known = document.getElementById("radio-known").checked;

  return { party: party, id: politician_id, known: known };
}

function create_radio_action(element) {
  return function (event) {
    console.log(element);
    let set_data = get_current_values();
    console.log(set_data);
    post("/guess_party", set_data);
  };
}

function load_data() {
  let info = get("/load_info");
  console.log(info);

  document
    .getElementById("abgeordneten-img")
    .setAttribute("src", `/static/${info.img}`);

  document.getElementById("politician_id").setAttribute("value", info.id);

  let guess = get(`/load_guess?id_=${info.id}`);

  if (!guess) {
    console.log("Found no guess");
    return;
  }

  console.log(guess);

  if (guess.known) {
    document.getElementById("radio-known").setAttribute("checked", "");
  }

  if (guess.party) {
    let id = `radio-${guess.party}`;
    for (input of document.getElementsByClassName("party-selector")) {
      if (input.getAttribute("id") === id) {
        input.setAttribute("checked", "");
      } else {
        input.removeAttribute("checked");
      }
    }
  }
}

selectors = document.getElementsByClassName("party-selector");
for (element of selectors) {
  element.addEventListener("click", create_radio_action(element));
}

document
  .getElementById("radio-known")
  .addEventListener("click", create_radio_action(null));

document.getElementById("refresh").addEventListener("click", function (event) {
  location.reload();
});

window.addEventListener("load", function (event) {
  load_data();
});

// .addEventListener("click", function(elem){
//     alert("click")
// })
