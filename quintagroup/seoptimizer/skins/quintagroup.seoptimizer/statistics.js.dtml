/******************************************************************
<dtml-with portal_properties>

Word Wrapping Rules:

    1. multiple spaces == one space 1
    2. word can include "-" and "'" // [\-\']
    3. token that not contain a-zA-Z0-9 symbols isn't a word
    4. non-word characters inside (or on the edge of) word divide it in smaller words

HTML code for text statistics: // for else fields than title in html code title will change accordingly to the field's id

  <div id="title-statistics" class="statistics">
      <span class="total-words">Total Words: <span class="value">5</span></span>
      <span class="stop-words">Stop Words: <span class="value">2</span></span>
      <span class="used-words">Used Words: <span class="value">3</span></span>
      <span class="length-words">Length: <span class="value">24</span></span>
  </div>

*******************************************************************/

<dtml-try>
var stop_words = <dtml-var expr="list(seo_properties.stop_words)">;
<dtml-except>
var stop_words = [];
</dtml-try>

<dtml-try>
var ids = <dtml-var expr="list(seo_properties.fields)">;
<dtml-except>
var ids = [];
</dtml-try>

var template = '<span class="total-words">Total Words: <span class="value">total_row</span></span> <span class="stop-words">Stop Words: <span class="value">stop_row</span></span> <span class="used-words">Used Words: <span class="value">used_row</span></span> <span class="length-words">Length: <span class="value">length_row</span></span>';

var stop_dict = {};

for (var j=0; word=stop_words[j]; j++) {stop_dict[word] = 1;};

function countWords(data) {
    var total = 0;
    var stop  = 0;
    var used  = 0;
    var len = data.length || 0;
    if (len != 0) {
        data = data // replace all non-word character with space
                   .replace(/[^a-zA-Z0-9\-\'\u2019\"\`]+/g, ' ')
                    // replace "-" and "'" symbols if it create groups event inside of token
                   .replace(/[\-\'\u2019\"\`]{2,}/g, ' ')
                    // replace all non-word characters and "-", "'" if it stay at word edge
                   .replace(/(?:^|\s+)[^a-zA-Z0-9]+|[^a-zA-Z0-9]+(?:\s+|$)/g, ' ')
                   // strip whitespaces
                   .replace(/^\s*(.*?)\s*$/, '$1');
        var data_list = data.split(/[^a-zA-Z0-9\-\'\u2019\"\`]+/);
        for (var i=0; word=data_list[i]; i++) {
            stop += stop_dict[word.toLowerCase()] ? 1:0;
        };
        total = data_list.length;
        used = total - stop;
    };
    return {'total': total, 'stop': stop, 'used': used, 'length': len};
};

function getHTML(source) {
    var stats = countWords(source);
    var html = template;
    for (var p in stats) {
        html = html.replace(p+'_row', stats[p]);
    };
    return html;
};

function listenField(event) {
    var event = event ? event:window.event;
    var target = null;
    if (event.target) {
        target = event.target;
    } else if (event.srcElement) {
        target = event.srcElement;
    };
    if (!target) {return false;};
    var update = document.getElementById(target.id+'-statistics');
    if (update) {
        update.innerHTML = getHTML(target.value||'');
    } else {
        window.status = "Couldn\'t find element with id = \'"+target.id+"-statistics\' on this page";
    };
};

function loadStatistics(event){
    for (var i=0; id=ids[i]; i++) {
        var el = document.getElementById(id);
        if (el && (typeof(el.value) != 'undefined')) {
            var div = document.createElement('DIV');
            div.id = id+'-statistics';
            div.className = 'statistics';
            div.innerHTML = getHTML(el.value||'');
            el.parentNode.insertBefore(div, el);
            registerEventListener(el, 'keyup', listenField);
        };
    };
};

registerPloneFunction(loadStatistics);
/*</dtml-with> Register onload function */