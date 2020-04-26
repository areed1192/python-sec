fetch("https://www.sec.gov/Archives/edgar/data/1326801/index.json", {
  "headers": {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "cookie": "_ga=GA1.2.860427492.1586098415; _gid=GA1.2.1206523834.1587272985; ak_bmsc=D4EA8957CFA51B5F5A33850E47707192B833CE372F3D0000EEDF9B5E8208C337~plXLc3VGQ6Dfwr4uQwAvBvbDY4oCNZp70TqRAocweVoXOVdiNpWq/J5QdDabOsQK+8RkUGkThHCRyORBurMqKgb/ghATgOte0mvYW7ZXc6fUyYuxLddbhuhvGivqP5+iqH27ME2NMUpRYB+VuQ88rsVSE0xqMxCCJALUJaeQkkNYoXtuwVcEJPVE1rNWomhmIEmE0zhcFXQboDnmd6eFNcfoJ0EpTqUB5+jCX11/yp9AQ=; _4c_=XZLbjoMgEIZfZcN1sYAcfZlGYaymB41S2W7Td99R25rUG%2BCfzy8y44OkBq6k4MoaYXKjlHVmR05wH0nxIEMb5mUiBQHtA4CVlPtSUlnVQB3UlgIDX9VeGiUt2ZHf1WVl7pwRzj53JFzfjgB1eTvHD2alco7n0gnE2j6%2BOKwwbZViWhv1xWrmZvZtLL9da31Im8pKzRUzjvENfSeI%2Bv6FPshtOKOyibEfi%2F0%2BpZSN4LNjN%2B0hHMthP0I5%2BGbd%2B%2B7Sl9f7GmVNvJzxS3wXAA3cZZxnHIP4h0cqBcN9P3Th5uMh3vsZSlD9jOGEhQBT6%2BGQ2hCb5e0Ff6UNtMcmzjGzS9wP8yHjbHlEbiW3au58aq%2BhS5vGSLWlH41Vgjw%2FY8J2cZU7jiOPES9vtVy0SEyfHuugWNBeU52rGievS1qBNLTOKycqk2Mgt8kL%2FIdmpXgpuV2Nz%2Bc%2F; _gat_UA-30394047-1=1; _gat_GSA_ENOR0=1; _gat_GSA_ENOR1=1"
  },
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors"
});

fetch("https://www.sec.gov/Archives/edgar/data/1326801/index.json", {
  "headers": {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
  },
  "referrerPolicy": "strict-origin-when-cross-origin",
  "body": null,
  "method": "GET",
  "mode": "cors",
  "credentials": "include"
});


// Invoke-WebRequest -Uri "https://www.sec.gov/Archives/edgar/data/1326801/index.json" -Headers @{
// "Cache-Control"="max-age=0"
//   "Upgrade-Insecure-Requests"="1"
//   "User-Agent"="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.14 Safari/537.36 Edg/83.0.478.10"
//   "Accept"="text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
//   "Sec-Fetch-Site"="none"
//   "Sec-Fetch-Mode"="navigate"
//   "Sec-Fetch-User"="?1"
//   "Sec-Fetch-Dest"="document"
//   "Accept-Encoding"="gzip, deflate, br"
//   "Accept-Language"="en-US,en;q=0.9"
//   "Cookie"="_ga=GA1.2.860427492.1586098415; _gid=GA1.2.1206523834.1587272985; ak_bmsc=D4EA8957CFA51B5F5A33850E47707192B833CE372F3D0000EEDF9B5E8208C337~plXLc3VGQ6Dfwr4uQwAvBvbDY4oCNZp70TqRAocweVoXOVdiNpWq/J5QdDabOsQK+8RkUGkThHCRyORBurMqKgb/ghATgOte0mvYW7ZXc6fUyYuxLddbhuhvGivqP5+iqH27ME2NMUpRYB+VuQ88rsVSE0xqMxCCJALUJaeQkkNYoXtuwVcEJPVE1rNWomhmIEmE0zhcFXQboDnmd6eFNcfoJ0EpTqUB5+jCX11/yp9AQ=; _4c_=XZLbjoMgEIZfZcN1sYAcfZlGYaymB41S2W7Td99R25rUG%2BCfzy8y44OkBq6k4MoaYXKjlHVmR05wH0nxIEMb5mUiBQHtA4CVlPtSUlnVQB3UlgIDX9VeGiUt2ZHf1WVl7pwRzj53JFzfjgB1eTvHD2alco7n0gnE2j6%2BOKwwbZViWhv1xWrmZvZtLL9da31Im8pKzRUzjvENfSeI%2Bv6FPshtOKOyibEfi%2F0%2BpZSN4LNjN%2B0hHMthP0I5%2BGbd%2B%2B7Sl9f7GmVNvJzxS3wXAA3cZZxnHIP4h0cqBcN9P3Th5uMh3vsZSlD9jOGEhQBT6%2BGQ2hCb5e0Ff6UNtMcmzjGzS9wP8yHjbHlEbiW3au58aq%2BhS5vGSLWlH41Vgjw%2FY8J2cZU7jiOPES9vtVy0SEyfHuugWNBeU52rGievS1qBNLTOKycqk2Mgt8kL%2FIdmpXgpuV2Nz%2Bc%2F; _gat_UA-30394047-1=1; _gat_GSA_ENOR0=1; _gat_GSA_ENOR1=1"
// }

// GET /Archives/edgar/data/1326801/index.json HTTP/1.1
// Host: www.sec.gov
// Connection: keep-alive
// Cache-Control: max-age=0
// Upgrade-Insecure-Requests: 1
// User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.14 Safari/537.36 Edg/83.0.478.10
// Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
// Sec-Fetch-Site: none
// Sec-Fetch-Mode: navigate
// Sec-Fetch-User: ?1
// Sec-Fetch-Dest: document
// Accept-Encoding: gzip, deflate, br
// Accept-Language: en-US,en;q=0.9
// Cookie: _ga=GA1.2.860427492.1586098415; _gid=GA1.2.1206523834.1587272985; ak_bmsc=D4EA8957CFA51B5F5A33850E47707192B833CE372F3D0000EEDF9B5E8208C337~plXLc3VGQ6Dfwr4uQwAvBvbDY4oCNZp70TqRAocweVoXOVdiNpWq/J5QdDabOsQK+8RkUGkThHCRyORBurMqKgb/ghATgOte0mvYW7ZXc6fUyYuxLddbhuhvGivqP5+iqH27ME2NMUpRYB+VuQ88rsVSE0xqMxCCJALUJaeQkkNYoXtuwVcEJPVE1rNWomhmIEmE0zhcFXQboDnmd6eFNcfoJ0EpTqUB5+jCX11/yp9AQ=; _4c_=XZLbjoMgEIZfZcN1sYAcfZlGYaymB41S2W7Td99R25rUG%2BCfzy8y44OkBq6k4MoaYXKjlHVmR05wH0nxIEMb5mUiBQHtA4CVlPtSUlnVQB3UlgIDX9VeGiUt2ZHf1WVl7pwRzj53JFzfjgB1eTvHD2alco7n0gnE2j6%2BOKwwbZViWhv1xWrmZvZtLL9da31Im8pKzRUzjvENfSeI%2Bv6FPshtOKOyibEfi%2F0%2BpZSN4LNjN%2B0hHMthP0I5%2BGbd%2B%2B7Sl9f7GmVNvJzxS3wXAA3cZZxnHIP4h0cqBcN9P3Th5uMh3vsZSlD9jOGEhQBT6%2BGQ2hCb5e0Ff6UNtMcmzjGzS9wP8yHjbHlEbiW3au58aq%2BhS5vGSLWlH41Vgjw%2FY8J2cZU7jiOPES9vtVy0SEyfHuugWNBeU52rGievS1qBNLTOKycqk2Mgt8kL%2FIdmpXgpuV2Nz%2Bc%2F; _gat_UA-30394047-1=1; _gat_GSA_ENOR0=1; _gat_GSA_ENOR1=1
