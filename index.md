<style>
table.dataframe, .dataframe th, .dataframe td {
  border: none;
  border-bottom: 1px solid #C8C8C8;
  border-collapse: collapse;
  text-align:left;
  padding: 10px;
  margin-bottom: 40px;
  font-size: 0.9em;
}
.dataframe summary {
  border: none;
  border-bottom: 1px solid #C8C8C8;
  border-collapse: collapse;
  text-align:left;
  padding: 10px;
  margin-bottom: 40px;
  font-size: 0.5em;
}
</style>

# Open Healthcare Statistics

<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: 2021-03-04 23:03:21</p>

---

<table border="1" class="dataframe summary">
  <thead>
    <tr style="text-align: right;">
      <th>Org</th>
      <th>Open Repos</th>
      <th>Total Size</th>
      <th>Stargazers</th>
      <th>Watchers</th>
      <th>Forks</th>
      <th>Open Issues</th>
      <th>Top License</th>
      <th>Top Language</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>111Online</th>
      <td>13</td>
      <td>520454</td>
      <td>10</td>
      <td>10</td>
      <td>0</td>
      <td>25</td>
      <td>Apache License 2.0</td>
      <td>C#</td>
    </tr>
    <tr>
      <th>NHSDigital</th>
      <td>79</td>
      <td>474111</td>
      <td>87</td>
      <td>87</td>
      <td>69</td>
      <td>326</td>
      <td>MIT License</td>
      <td>Python</td>
    </tr>
    <tr>
      <th>nhsconnect</th>
      <td>177</td>
      <td>3173655</td>
      <td>239</td>
      <td>239</td>
      <td>197</td>
      <td>385</td>
      <td>Apache License 2.0</td>
      <td>CSS</td>
    </tr>
    <tr>
      <th>nhsengland</th>
      <td>23</td>
      <td>36119</td>
      <td>13</td>
      <td>13</td>
      <td>38</td>
      <td>79</td>
      <td>MIT License</td>
      <td>Python</td>
    </tr>
    <tr>
      <th>nhsx</th>
      <td>42</td>
      <td>541270</td>
      <td>2384</td>
      <td>2384</td>
      <td>537</td>
      <td>82</td>
      <td>MIT License</td>
      <td>Kotlin</td>
    </tr>
  </tbody>
</table>

---

<!--
## [NHSX](https://github.com/nhsx)

#### Logo

<img src="https://avatars.githubusercontent.com/u/47388472?v=4" width="50"/>

### Open Repos

<div id="NHSX"></div>
<script>
    fetch('github_api/nhsx_repos.json')
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
        var mainContainer = document.getElementById("NHSX");
        for (var i = 0; i < data.length; i++) {
            var div = document.createElement("div");
            div.innerHTML = data[i].name;
            mainContainer.appendChild(div);
        }
    }
</script>-->
