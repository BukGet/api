            <div class="package">
                <div class="header">
                    <div class="wrapper"> 
                        <h1>{{name}}</h1>
                        <div class="desc">{{description}}</div>
                    </div>
                </div>
                
                <div class="meta rounded-five">pkg install {{name}}{{#versions}}<span class="hidden v{{version_u}}">@{{version}}</span>{{/versions}}</div>
                
                <div class="wrapper">
                    <div class="versions grid_10">
                        <h2 class="top-rounded-five">Versions</h2>
                        <ul>
                        {{#versions}}
                            <li><a href="#/package/{{name}}/{{version}}" id="v" version="{{version_u}}" class="{{version_u}}">{{version}}</a></li>
                        {{/versions}}
                        {{^versions}}
                            <li>No versions found</li>
                        {{/versions}}
                        </ul>
                    </div>
                    {{#versions}}
                    <div class="info v{{version_u}} grid_10">
                        <a href="{{location}}" class="buttons cancel download">Download {{version}}</a>
                        
                        <div class="item"><span>Works With:</span> {{#engines}}{{name}} ({{min}} - {{max}}), {{/engines}}</div>
                        <div class="item"><span>Branch:</span> {{branch}}</div>
                        <div class="item"><span>Checksum:</span> {{checksum}}</div>
                        <div class="item"><span>Required Dependencies:</span> {{#required_dependencies}}{{.}}, {{/required_dependencies}}{{^required_dependencies}}None{{/required_dependencies}}</div>
                        <div class="item"><span>Optional:</span> {{#optional_dependencies}}{{.}}, {{/optional_dependencies}}{{^optional_dependencies}}None{{/optional_dependencies}}</div>
                    </div>
                    {{/versions}}
                    {{^versions}}
                    <div class="info show grid_10">
                        Nothing found.
                    </div>
                    {{/versions}}
                </div>
            </div>