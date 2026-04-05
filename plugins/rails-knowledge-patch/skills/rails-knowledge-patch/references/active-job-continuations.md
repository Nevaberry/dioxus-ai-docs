# Active Job Continuations (8.1)

Long-running jobs broken into resumable steps. Include `ActiveJob::Continuable`:

```ruby
class ProcessImportJob < ApplicationJob
  include ActiveJob::Continuable

  def perform(import_id)
    @import = Import.find(import_id)

    step :initialize do
      @import.initialize
    end

    step :process do |step|
      @import.records.find_each(start: step.cursor) do |record|
        record.process
        step.advance! from: record.id
      end
    end

    step :finalize  # calls private method
  end

  private
    def finalize
      @import.finalize
    end
end
```

Steps run in order. If a job is interrupted (timeout, crash), it resumes from the last completed step. The `step.advance!` call within a step saves cursor position for mid-step resumption.
