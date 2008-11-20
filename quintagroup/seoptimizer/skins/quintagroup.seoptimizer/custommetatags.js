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