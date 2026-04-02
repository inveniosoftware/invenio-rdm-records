import React, { useState } from "react";
import { Grid, Button, Icon, Message, Input } from "semantic-ui-react";
import PropTypes from "prop-types";
import { ParentSize } from "@visx/responsive";
import { QuotaDisplay } from "./QuotaDisplay";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { ErrorMessage, http, withCancel } from "react-invenio-forms";
import { saveAndFetchDraft } from "../../../state/actions";
import { connect } from "react-redux";

export const QuotaManagerComponent = (props) => {
  const { draft, quota, toggleQuotaSection, additionalQuota, setAdditionalQuota } =
    props;
  const { defaultStorage, additionalStorage, maxAdditionalStorage, remainingStorage } =
    quota;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    setLoading(true);
    const { additionalQuota, saveAndFetchDraftAction } = props;
    const payload = {
      quota_size: (defaultStorage + additionalQuota).toString(),
    };

    const savedDraft = await saveAndFetchDraftAction(draft); // we require the recid to be reserved

    const quotaIncreaseEndpoint = savedDraft.links?.quota_increase;

    if (!quotaIncreaseEndpoint) {
      setLoading(false);
      setError(i18next.t("Could not submit the quota increase request"));
      return;
    }

    const cancellableAction = withCancel(http.post(quotaIncreaseEndpoint, payload));
    try {
      const response = await cancellableAction.promise;
      const data = response.data;

      if (response.status === 200) {
        window.location.reload();
      } else if (response.status === 201) {
        window.location.href = data.links.self_html;
      }
    } catch (error) {
      setError(error);
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid.Column width={16}>
      <Message className="pt-20 pb-20">
        <Grid>
          <Grid.Column width={15} className="pt-0">
            <strong>{i18next.t("Manage storage")}</strong>
          </Grid.Column>
          <Grid.Column width={1} className="pt-0">
            <Icon
              name="close"
              className="right-floated link"
              onClick={() => toggleQuotaSection()}
            />
          </Grid.Column>
        </Grid>
        {remainingStorage > 0 ? (
          <Message info>
            {i18next.t(
              "Each record has a default quota of {{defaultStorage}} GB. You have an additional allowance of up to {{maxAdditionalStorage}} GB that can be distributed across your uploads as needed.",
              {
                defaultStorage: defaultStorage,
                maxAdditionalStorage: maxAdditionalStorage,
              }
            )}
          </Message>
        ) : (
          <Message warning className="display">
            {i18next.t(
              "Each record has a default quota of {{defaultStorage}} GB. You have already used your additional allowance of {{maxAdditionalStorage}} GB across your uploads.",
              {
                defaultStorage: defaultStorage,
                maxAdditionalStorage: maxAdditionalStorage,
              }
            )}
          </Message>
        )}
        {/* Progress bar */}
        <ParentSize>
          {({ width, height }) => (
            <QuotaDisplay
              width={width}
              height={40}
              quota={quota}
              additionalQuota={additionalQuota}
            />
          )}
        </ParentSize>
        {remainingStorage > 0 && (
          <>
            <div className="flex align-items-center justify-space-between mt-25">
              <strong id="additional-storage">{i18next.t("Additional storage")}</strong>

              <Input
                size="small"
                aria-labelledby="additional-storage"
                type="number"
                value={additionalQuota}
                onChange={(e, { k, value }) => setAdditionalQuota(parseInt(value))}
                disabled={loading}
              />
            </div>

            <Input
              value={additionalQuota}
              onChange={(e, { k, value }) => setAdditionalQuota(parseInt(value))}
              min={0}
              max={Math.min(maxAdditionalStorage, remainingStorage)}
              name="quota"
              step={1}
              type="range"
              style={{ width: "100%" }}
              disabled={loading}
            />
            <div className="flex align-items-center justify-space-between pb-20">
              <div>0 GB</div>
              <div>
                {i18next.t("New total:")}{" "}
                <strong>{defaultStorage + additionalQuota} GB</strong>
              </div>
              <div>{remainingStorage} GB</div>
            </div>
            {error && (
              <ErrorMessage
                header={i18next.t("Unable to increase quota")}
                content={i18next.t(error)}
                icon="exclamation"
                className="text-align-left"
                negative
              />
            )}
            <div className="flex justify-end">
              <Button
                type="button"
                color="green"
                labelPosition="left"
                icon="check"
                content={i18next.t("Apply")}
                onClick={() => handleSubmit()}
                loading={loading}
                disabled={loading || additionalQuota === additionalStorage}
              />
            </div>
          </>
        )}
      </Message>
    </Grid.Column>
  );
};

QuotaManagerComponent.propTypes = {
  draft: PropTypes.object.isRequired,
  quota: PropTypes.object.isRequired,
  toggleQuotaSection: PropTypes.func.isRequired,
  additionalQuota: PropTypes.number.isRequired,
  setAdditionalQuota: PropTypes.func.isRequired,
  saveAndFetchDraftAction: PropTypes.func.isRequired,
};

const mapDispatchToProps = (dispatch) => ({
  saveAndFetchDraftAction: (values) => dispatch(saveAndFetchDraft(values)),
});

export const QuotaManager = connect(null, mapDispatchToProps)(QuotaManagerComponent);
