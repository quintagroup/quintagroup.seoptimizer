/******************************************************************/

var seo_keywords_url = '&dtml-absolute_url;/checkSEOKeywords';
var KEYWORDS_IDS = ['seo_keywords',];
// var KEYWORDS_REPORT = {};

// function extractWords(data) {
//     data = data // replace all non-word character with space
//                 .replace(/[^a-zA-Z0-9\-\'\u2019\"\`]+/g, ' ')
//                 // replace "-" and "'" symbols if it create groups event inside of token
//                 .replace(/[\-\'\u2019\"\`]{2,}/g, ' ')
//                 // replace all non-word characters and "-", "'" if it stay at word edge
//                 .replace(/(?:^|\s+)[^a-zA-Z0-9]+|[^a-zA-Z0-9]+(?:\s+|$)/g, ' ')
//                 // strip whitespaces
//                 .replace(/^\s*(.*?)\s*$/, '$1');
//     return data.split(/[^a-zA-Z0-9\-\'\u2019\"\`]+/);
// }
// 
// function countTerm(node, word, id) {
//     var contents = extractWords(node.nodeValue.toLowerCase());
//     var term = word.toLowerCase();
//     for (var i = 0, w; w = contents[i]; i++) {
//         if (w == term) {
//             KEYWORDS_REPORT[id][word] = 1;
//             return 'found';
//         }
//     }
//     return false;
// }
// 
// function keywordsWalkTextNodes(node, func, data, id) {
//     if (!node) return false;
//     if (KEYWORDS_REPORT[id][data] == 1) return 'found';
//     if (node.hasChildNodes) {
//         if (node.nodeType == 3) {
//             if (func(node, data, id) == 'found') {
//                 return 'found';
//             }
//         }
//         for (var i = 0; i < node.childNodes.length; i++) {
//             if (keywordsWalkTextNodes(node.childNodes[i], func, data, id) == 'found') {
//                 return 'found';
//             }
//         }
//     }
// }

// function checkPageKeywords(event) {
//     var event = event ? event:window.event;
//     var target = event.target ? event.target : event.srcElement;
//     if (!target) {return false;};
//     var id = target.id.replace('_check_keywords', '')
//     KEYWORDS_REPORT[id] = {};
//     var area = document.getElementById(id);
//     if (area && typeof(area.value) != 'undefined') {
//         var terms = extractWords(area.value);
//         for (var i = 0, term; term = terms[i]; i++) {
//             if (KEYWORDS_REPORT[id][term] == 1) continue;
//             KEYWORDS_REPORT[id][term] = 0;
//             keywordsWalkTextNodes(document.body, countTerm, term, id);
//         }
//     }
//     var report = '';
//     for (var term in KEYWORDS_REPORT[id]) {
//         if (KEYWORDS_REPORT[id][term] != 1)
//             report += term + ' ';
//     }
//     KEYWORDS_REPORT[id] = {};
//     if (report != '') {
//         report = 'Next keywords did not appear on the page:\n' + report;
//     } else {
//         report = 'All keywords found on the page!';
//     }
//     alert(report);
//     return false;
// }

function checkPageKeywords(event) {
    var event = event ? event:window.event;
    var target = event.target ? event.target : event.srcElement;
    if (!target) {return false;};
    var id = target.id.replace('_check_keywords', '')
    var area = document.getElementById(id);
    if (area && typeof(area.value) != 'undefined') {
        var req = new XMLHttpRequest();
        req.open("POST", seo_keywords_url, true);
        req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        req.onreadystatechange = function(request) {
            if (req.readyState == 4) {
                if (req.status == '200') {
                    alert(req.responseText);
                } else {
                    alert('Error on server!');
                }
            }
        };
        req.send("text="+area.value);
    }
    return false;
}

function addSeoKeywordsButton(event) {
    for (var i = 0, id; id = KEYWORDS_IDS[i]; i++) {
        var area = document.getElementById(id);
        if (!area || (typeof(area.value) == 'undefined')) continue;
        var button = document.createElement('INPUT');
        button.type = 'button';
        button.value = 'Check Keywords';
        button.name = id+'_check_keywords';
        button.id = id+'_check_keywords';
        button.className = 'check-keywords-button';
        area.parentNode.insertBefore(button, area.nextSibling.nextSiblin);
        registerEventListener(button, 'click', checkPageKeywords);
//         KEYWORDS_REPORT[id] = {};
    }
}

registerPloneFunction(addSeoKeywordsButton);
