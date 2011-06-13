<div class="logdata">
%for line in logdata.split('\n'):
  %if len(line) > 0:
  <span><em>{{!line.replace('ve513 bukget: ','</em> ')}}</span>
  %end
%end
</div>
%rebase layout title="Logs"

