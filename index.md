<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>

# Open Source Healthcare Statistics

### Collecting statistics on open source NHS and healthcare related code repositories

Open source is the practice of publishing the source code of a software project so that anyone can read, modify, re-use, and improve that software.

As set out in the [NHS Digital Service Manual](https://service-manual.nhs.uk/service-standard/12-make-new-source-code-open), public services are built with public money--so unless there's a good reason not to (for security reasons for example), all code produced by the NHS should be made publicly available. To this end, the [Department of Health & Social Care has recently made a commitment](https://www.gov.uk/government/publications/data-saves-lives-reshaping-health-and-social-care-with-data-draft/data-saves-lives-reshaping-health-and-social-care-with-data-draft) to make all new NHS code open source and published under appropriate licences (such as [MIT](https://opensource.org/licenses/MIT) and [OGLv3](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)).

<hr class="nhsuk-u-margin-top-0 nhsuk-u-margin-bottom-6">

## Open Health Repository Statistics

{% include update.html %}
{% include NHSUK_table.html %}

<div class="nhsuk-action-link">
  <a class="nhsuk-action-link__link" href="assets/data/openhealthstats.csv">
    <svg class="nhsuk-icon nhsuk-icon__arrow-right-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 2a10 10 0 0 0-9.95 9h11.64L9.74 7.05a1 1 0 0 1 1.41-1.41l5.66 5.65a1 1 0 0 1 0 1.42l-5.66 5.65a1 1 0 0 1-1.41 0 1 1 0 0 1 0-1.41L13.69 13H2.05A10 10 0 1 0 12 2z"></path>
    </svg>
    <span class="nhsuk-action-link__text">Download this data</span>
  </a>
</div>

## Charts

{% include plotly_chart.html %}

<hr class="nhsuk-u-margin-top-6 nhsuk-u-margin-bottom-6">

## About this page

This tool is built using end-to-end open source analytical tools including: [The NHS Digital Service Manual](https://service-manual.nhs.uk/), [python](https://nhs-pycom.net/), [plotly](https://plotly.com/python/), [github.io](https://pages.github.com/), and [github actions](https://github.com/features/actions).

<div class="nhsuk-action-link">
  <a class="nhsuk-action-link__link" href="/open-health-statistics/blog">
    <svg class="nhsuk-icon nhsuk-icon__arrow-right-circle" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-hidden="true">
      <path d="M0 0h24v24H0z" fill="none"></path>
      <path d="M12 2a10 10 0 0 0-9.95 9h11.64L9.74 7.05a1 1 0 0 1 1.41-1.41l5.66 5.65a1 1 0 0 1 0 1.42l-5.66 5.65a1 1 0 0 1-1.41 0 1 1 0 0 1 0-1.41L13.69 13H2.05A10 10 0 1 0 12 2z"></path>
    </svg>
    <span class="nhsuk-action-link__text">Find out how to build your own open analytics pipeline</span>
  </a>
</div>

To get your organisation added to the collection, email: <a href="mailto:craig.shenton@nhsx.nhs.uk">craig.shenton@nhsx.nhs.uk</a>
