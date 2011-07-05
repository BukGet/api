            <div class="wrapper">
                <div class="side-bar">
                    <input type="search" results="5" class="s" placeholder="Search.." class="rounded-three">
                </div>
                
                <div class="pack-list">
                    {foreach $packages as $i => $pack}
                    <div class="pack" onClick="window.location = '#/package/{$pack.name}';">
                        <div class="categories">
                            {$categories=$pack.categories}
                            {foreach $categories as $i => $category}
                                <a href="#" class="buttons small">{$category}</a>
                            {foreachelse}
                                ...
                            {/foreach}
                        </div>
                        <span class="name">{$pack.name}</span>
                        <div class="description">
                            <span class="maintainer">Maintained by: {$pack.maintainer}</span>
                            <span class="desc">{$pack.description}</span>
                        </div>
                    </div>
                    {foreachelse}
                    <div class="error">
                        <span class="description">No Results</span>
                    </div>
                    {/foreach}
                </div>
            </div>