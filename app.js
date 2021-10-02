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
  let id = document.getElementById("politician_id").getAttribute("value");

  let guess = get(`/load_guess?id_=${id}`);

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

function restore_toogle_state() {
  let enabled_value = "show-only-unlabeled=true";
  let disabled_value = "show-only-unlabeled=false";
  let checkbox = document.getElementById("radio-show-only-unlabeled");

  if (document.cookie == enabled_value) {
    checkbox.setAttribute("checked", "");
  } else {
    checkbox.removeAttribute("checked");
  }
}

selectors = document.getElementsByClassName("party-selector");
for (element of selectors) {
  element.addEventListener("click", create_radio_action(element));
}

document
  .getElementById("radio-known")
  .addEventListener("click", create_radio_action(null));

document.getElementById("random").addEventListener("click", function (event) {
  let only_unknown = document.cookie === "show-only-unlabeled=true";
  console.log(only_unknown);
  let random_id = get(`/random_id?load_only_unknown=${only_unknown}`);
  window.location.href = window.location.origin + `?id_=${random_id}`;
});

window.addEventListener("load", function (event) {
  load_data();
  restore_toogle_state();
});

document
  .getElementById("radio-show-only-unlabeled")
  .addEventListener("click", function () {
    let enabled_value = "show-only-unlabeled=true";
    let disabled_value = "show-only-unlabeled=false";
    let old_value = document.cookie;
    console.log("Cookie:", old_value);

    if (old_value == enabled_value) {
      document.cookie = disabled_value;
    } else {
      document.cookie = enabled_value;
    }
  });
