# Open Healthcare Statistics

<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: 2021-03-04 10:53:21</p>

---

## Sub Heading

### Open Repos

[![View on GitHub](https://img.shields.io/badge/GitHub-View_on_GitHub-blue?logo=GitHub)](https://github.com/nhsx/open-health-statistics)

**Bold:** test

<center><img src="https://avatars.githubusercontent.com/u/47388472?v=4" width="50"/></center>

---

### Section

[![View on GitHub](https://img.shields.io/badge/GitHub-View_on_GitHub-blue?logo=GitHub)](https://github.com/nhsx/open-health-statistics)

**Bold:** test

<center><img src="https://avatars.githubusercontent.com/u/47388472?v=4" width="50"/></center>

<div id="myData"></div>
<script>
    fetch('https://api.github.com/orgs/nhsx/repos.json')
        .then(function (response) {
            return response.json();
        })
        .then(function (data) {
            appendData(data);
        })
        .catch(function (err) {
            console.log('error: ' + err);
        });
    function appendData(data) {
        var mainContainer = document.getElementById("myData");
        for (var i = 0; i < data.length; i++) {
            var div = document.createElement("div");
            div.innerHTML = 'Name: ' + data[i].name + ' ' + data[i].html_url;
            mainContainer.appendChild(div);
        }
    }
</script>

---

<center>footer</center>
