            <div class="wrapper">
                <div class="side-bar">
                    <input type="search" results="5" class="s" placeholder="Search.." class="rounded-three">
                </div>
                
                <div class="pack-list">
                    {{#packages}}
                    <div class="pack" onClick="window.location = '#/package/{{name}}';">
                        <div class="categories">
                            {{#categories}}<a href="#" class="buttons small">{{.}}</a> {{/categories}}
                            {{^categories}}...{{/categories}}
                        </div>
                        <span class="name">{{name}}</span>
                        <div class="description">
                            <span class="maintainer">Maintained by: {{maintainer}}</span>
                            <span class="desc">{{description}}</span>
                        </div>
                    </div>
                    {{/packages}}
                    {{^packages}}
                    <div class="error">
                        <span class="description">No Results</span>
                    </div>
                    {{/packages}}
                </div>
            </div>