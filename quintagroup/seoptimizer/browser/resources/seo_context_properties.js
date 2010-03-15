/******************************************************************

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

// stop_words and ids defined in the browser/templates/seo_context_properties.pt
// page template and here we use already calculated variables

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


/******************************************************************

Adding 'Check Keywords' button to check whether words you entered in
this block as SEO keywords are present in content.

*******************************************************************/

var seo_keywords_url = document.baseURI + '/@@checkSEOKeywords';
var KEYWORDS_IDS = ['seo_keywords',];

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
    }
}

registerPloneFunction(addSeoKeywordsButton);

/******************************************************************

Using for manage your custom meta tags, to be added to the global Meta Tags.

*******************************************************************/

customMetaTagsFunctions = new Object()

customMetaTagsFunctions.getInputOrSelect = function(node) {
    /* Get the (first) input or select form element under the given node */
    
    var inputs = node.getElementsByTagName("input");
    if(inputs.length > 0) {
        return inputs[0];
    }
    
    var selects = node.getElementsByTagName("select");
    if(selects.length > 0) {
        return selects[0];
    }

    return null;
}

customMetaTagsFunctions.getWidgetRows = function(currnode) {
  /* Return primary <tr>s of current node's parent DGW */
  tbody = this.getParentElementById(currnode, "datagridwidget-tbody");
  return this.getRows(tbody);
}

customMetaTagsFunctions.getRows = function(tbody) {
  /* Return <tr> rows of <table> element */
    
  var rows = new Array()
  
  child = tbody.firstChild;
  while(child != null) {
    if(child.tagName != null) {
      if(child.tagName.toLowerCase() == "tr") {
        rows = rows.concat(child);
      }
    }
    child = child.nextSibling;
  }
                
  return rows;   
} 

customMetaTagsFunctions.autoInsertRow = function(e) {
    /* Add a new row when changing the last row 
       (i.e. the infamous auto insert feature)
    
       Check that if this onchange event handler was
       called from the last row. In this case,
       add a new row for DGF.
       
    */

    var currnode = window.event ? window.event.srcElement : e.currentTarget;
    
  // fetch required data structure   
    var tbody = this.getParentElement(currnode, "TBODY");
    var rows = this.getRows(tbody);        
    var lastRow = rows[rows.length-1]; 
    
    var thisRow = this.getParentElementById(currnode, "datagridwidget-row");      
    
    /* Skip the very last row which is a hidden template row */
    if(rows.length-1 ==(thisRow.rowIndex)) {
      // Create a new row
      var newtr = this.createNewRow(lastRow);
                                                          
      // Put new row to DOM tree before template row        
    lastRow.parentNode.insertBefore(newtr, lastRow);
    
    // update orderindex hidden fields
    this.updateOrderIndex(tbody);               
    }    
}

customMetaTagsFunctions.addRowAfter = function(currnode) {
  /*
    Creates a new row before the clicked row
  */
  
  // fetch required data structure
    var tbody = this.getParentElementById(currnode, "datagridwidget-tbody"); 
    var thisRow = this.getParentElementById(currnode, "datagridwidget-row"); 

    var newtr = this.createNewRow(thisRow);
        
  thisRow.parentNode.insertBefore(newtr, thisRow);
  
  // update orderindex hidden fields
  this.updateOrderIndex(tbody); 
  
}

customMetaTagsFunctions.addRow = function(id) {
  /* Explitcly add row for given DataGridField 
  
    @param id Archetypes field id for the widget  
  */
  
  // fetch required data structure
    var tbody = document.getElementById("datagridwidget-tbody-" + id);    
    var rows = this.getRows(tbody);    
    var lastRow = rows[rows.length-1];
        
    var oldRows = rows.length;
                  
    // Create a new row
    var newtr = this.createNewRow(lastRow);
    
    // Put new row to DOM tree before template row        
  newNode = lastRow.parentNode.insertBefore(newtr, lastRow);
  
  // update orderindex hidden fields
  this.updateOrderIndex(tbody);   
      
}

customMetaTagsFunctions.createNewRow = function(tr) { 
  /* Creates a new row 
       
     @param tr A row in a table where we'll be adding the new row
  */
  
    var tbody = this.getParentElementById(tr, "datagridwidget-tbody"); 
    var rows = this.getRows(tbody);   
    
    // hidden template row 
    var lastRow = rows[rows.length-1]; 
  
  var newtr = document.createElement("tr");
    newtr.setAttribute("id", "datagridwidget-row");
    newtr.setAttribute("class", "datagridwidget-row");
      
  // clone template contents from the last row to the newly created row
  // HOX HOX HOX
  // If f****ng IE clones lastRow directly it doesn't work.
  // lastRow is in hidden state and no matter what you do it remains hidden.
  // i.e. overriding class doesn't bring it visible.
  // In Firefox everything worked like a charm.
  // So the code below is really a hack to satisfy Microsoft codeborgs.
  // keywords: IE javascript clone clonenode hidden element render visibility visual
  child = lastRow.firstChild;
  while(child != null) {
    newchild = child.cloneNode(true);
    newtr.appendChild(newchild);
    child = child.nextSibling;
  }   
      
    return newtr;  
}


customMetaTagsFunctions.removeFieldRow = function(node) {
    /* Remove the row in which the given node is found */
    
    var row = this.getParentElementById(node, 'datagridwidget-row');
    var tbody = this.getParentElementById(node, 'datagridwidget-tbody');
    tbody.removeChild(row);
}

customMetaTagsFunctions.moveRowDown = function(currnode){
    /* Move the given row down one */
           
    var tbody = this.getParentElementById(currnode, "datagridwidget-tbody");    
    
    var rows = this.getWidgetRows(currnode);
    
    var row = this.getParentElementById(currnode, "datagridwidget-row");      
    if(row == null) {
      alert("Couldn't find DataGridWidget row");
      return;
    }
    
    var idx = null
    
    // We can't use nextSibling because of blank text nodes in some browsers
    // Need to find the index of the row
    for(var t = 0; t < rows.length; t++) {
        if(rows[t] == row) {
            idx = t;
            break;
        }
    }

    // Abort if the current row wasn't found
    if(idx == null)
        return;     
        
    // If this was the last row (before the blank row at the end used to create
    // new rows), move to the top, else move down one.
    if(idx + 2 == rows.length) {
        var nextRow = rows.item[0]
        this.shiftRow(row, nextRow)
    } else {
        var nextRow = rows[idx+1]
        this.shiftRow(nextRow, row)
    }
    
    this.updateOrderIndex(tbody)

}

customMetaTagsFunctions.moveRowUp = function(currnode){
    /* Move the given row up one */
    
    var tbody = this.getParentElementById(currnode, "datagridwidget-tbody");    
    var rows = this.getWidgetRows(currnode);
    
    var row = this.getParentElementById(currnode, "datagridwidget-row");      
    if(row == null) {
      alert("Couldn't find DataGridWidget row");
      return;
    }

    var idx = null
    
    // We can't use nextSibling because of blank text nodes in some browsers
    // Need to find the index of the row
    for(var t = 0; t < rows.length; t++) {
        if(rows[t] == row) {
            idx = t;
            break;
        }
    }
    
    // Abort if the current row wasn't found
    if(idx == null)
        return;
        
    // If this was the first row, move to the end (i.e. before the blank row
    // at the end used to create new rows), else move up one
    if(idx == 0) {
        var previousRow = rows[rows.length - 1]
        this.shiftRow(row, previousRow);
    } else {
        var previousRow = rows[idx-1];
        this.shiftRow(row, previousRow);
    }
    
    this.updateOrderIndex(tbody);
}

customMetaTagsFunctions.shiftRow = function(bottom, top){
    /* Put node top before node bottom */
    
    bottom.parentNode.insertBefore(bottom, top)   
}

customMetaTagsFunctions.updateOrderIndex = function (tbody) {

    /* Update the hidden orderindex fields to be in the right order */
    
    var xre = new RegExp(/^orderindex__/)
    var idx = 0;
    var cell;
    
    var rows = this.getRows(tbody); 
    
    /* Make sure that updateOrderIndex doesn't touch 
       the template (last) row */
    for(var i=0; i<rows.length-1; i++) {
    
      for (var c = 0; (cell = rows[i].getElementsByTagName('INPUT').item(c)); c++) {
              
          if (cell.getAttribute('id')) {
              if (xre.exec(cell.id)) {
                  cell.value = idx;
              }
          }           
          this.updateRadioButtonGroupName(this.getParentElement(cell, "TR"), idx);        
          idx++;
      }      
  }
}


customMetaTagsFunctions.updateRadioButtonGroupName = function (row, newIndex) {
  /* Adjust radio button group names after reordering 
  
     Why we do this, see RadioColumn class comments
     
     TODO: If chain onchange -> updateOrderIndex -> updaterRadioButtonGroupName
     is triggered on Firefox, the value of checked radio button is put to the
     newly generated row instead of clicked row.
  */

   var cell;
   var xre = new RegExp(/^radio/)
   var xre2 = new RegExp(/^checkbox/)
   
    for (var c = 0; (cell = row.getElementsByTagName('INPUT').item(c)); c++) {
              
        if(cell.getAttribute('type')) {
          var type = cell.getAttribute('type');
             if (xre.exec(type) || xre2.exec(type)) {          
              
        var name = cell.getAttribute("NAME")
        if(name == null) continue;

        // save fieldId + columnId part
        var baseLabel = name.substring(0, name.lastIndexOf("."));       
        // update per row running id
        cell.setAttribute("NAME", baseLabel + "." + newIndex);
      }
        }               
  }
}

customMetaTagsFunctions.getParentElement = function(currnode, tagname) {
    /* Find the first parent node with the given tag name */

    tagname = tagname.toUpperCase();
    var parent = currnode.parentNode;

    while(parent.tagName.toUpperCase() != tagname) {
        parent = parent.parentNode;
        // Next line is a safety belt
        if(parent.tagName.toUpperCase() == "BODY") 
            return null;
    }

    return parent;
}

customMetaTagsFunctions.getParentElementById = function(currnode, id) {
    /* Find the first parent node with the given id 
    
      Id is partially matched: the beginning of
      an element id matches parameter id string.
    
      Currnode: Node where ascending in DOM tree beings
      Id: Id string to look for. 
            
    */
    
    id = id.toLowerCase();
    var parent = currnode.parentNode;

    while(true) {
       
      var parentId = parent.getAttribute("id");
      if(parentId != null) {      
         if(parentId.toLowerCase().substring(0, id.length) == id) break;
      }
          
        parent = parent.parentNode;
        // Next line is a safety belt
        if(parent.tagName.toUpperCase() == "BODY") 
            return null;
    }

    return parent;
}
