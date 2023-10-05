// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isEmpty from "lodash/isEmpty";
import _ from "lodash";
import {
  DISCARD_PID_FAILED,
  DISCARD_PID_STARTED,
  DISCARD_PID_SUCCEEDED,
  DRAFT_DELETE_FAILED,
  DRAFT_DELETE_STARTED,
  DRAFT_FETCHED,
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_PREVIEW_FAILED,
  DRAFT_PREVIEW_STARTED,
  DRAFT_PUBLISH_FAILED,
  DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
  DRAFT_PUBLISH_STARTED,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_STARTED,
  DRAFT_SAVE_SUCCEEDED,
  DRAFT_SUBMIT_REVIEW_FAILED,
  DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS,
  DRAFT_SUBMIT_REVIEW_STARTED,
  RESERVE_PID_FAILED,
  RESERVE_PID_STARTED,
  RESERVE_PID_SUCCEEDED,
  SET_COMMUNITY,
} from "../types";

async function changeURLAfterCreation(draftURL) {
  window.history.replaceState(undefined, "", draftURL);
}

export const saveDraftWithUrlUpdate = async (draft, draftsService) => {
  const hasAlreadyId = !!draft.id;
  const response = await draftsService.save(draft);

  const draftHasValidationErrors = !_isEmpty(response.errors);

  // In case of invalid values, on the second draft save, the form doesn't report the errors. This happens
  // because the backend doesn't save invalid metadata. Here we are merging draft state with backend
  // response in order not to lose those invalid values from the form state and have the errors reported.
  if (draftHasValidationErrors) {
    const mergingValues = {
      metadata: draft.metadata,
      custom_fields: draft.custom_fields,
    };

    response.data = _.merge(response.data, mergingValues);
  }

  if (!hasAlreadyId) {
    // draft was created, change URL to add the draft PID
    const draftURL = response.data.links.self_html;
    changeURLAfterCreation(draftURL);
  }
  return response;
};

async function _saveDraft(
  draft,
  draftsService,
  { depositState, dispatchFn, failType, partialValidationActionType }
) {
  let response;

  try {
    response = await saveDraftWithUrlUpdate(draft, draftsService, failType);
  } catch (error) {
    dispatchFn({
      type: failType,
      payload: { errors: error.errors },
    });
    throw error;
  }

  const draftHasValidationErrors = !_isEmpty(response.errors);
  const draftValidationErrorResponse = draftHasValidationErrors ? response : {};

  const {
    actions: { communityStateMustBeChecked, shouldDeleteReview, shouldUpdateReview },
    selectedCommunity,
  } = depositState.editorState;

  if (communityStateMustBeChecked) {
    const draftWithLinks = response.data;

    if (shouldDeleteReview) {
      // TODO handle global error here
      await draftsService.deleteReview(draftWithLinks.links);
    }
    if (shouldUpdateReview) {
      // TODO handle global error here
      await draftsService.createOrUpdateReview(
        draftWithLinks.links,
        selectedCommunity.id
      );
    }

    // fetch the draft after having changed the review request
    // to have the `review` field updated
    response = await draftsService.read(draftWithLinks.links);
    dispatchFn({
      type: DRAFT_FETCHED,
      payload: { data: response.data },
    });

    // previously saved data should be overriden by the latest read draft
    // Otherwise when the draft is partially saved, the community state will
    // not be taken into account
    draftValidationErrorResponse.data = {
      ...draftValidationErrorResponse.data,
      ...response.data,
    };
  }
  // Throw validation errors from the partially saved draft
  if (draftHasValidationErrors) {
    dispatchFn({
      type: partialValidationActionType,
      payload: {
        data: draftValidationErrorResponse.data,
        errors: draftValidationErrorResponse.errors,
      },
    });
    throw draftValidationErrorResponse;
  }

  return response;
}

export const save = (draft) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_SAVE_STARTED,
    });
    let response;

    response = await _saveDraft(draft, config.service.drafts, {
      depositState: getState().deposit,
      dispatchFn: dispatch,
      failType: DRAFT_SAVE_FAILED,
      partialValidationActionType: DRAFT_HAS_VALIDATION_ERRORS,
    });

    dispatch({
      type: DRAFT_SAVE_SUCCEEDED,
      payload: { data: response.data },
    });
  };
};

export const publish = (draft, { removeSelectedCommunity = false }) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_PUBLISH_STARTED,
    });

    if (removeSelectedCommunity) {
      // we set the community to null so we delete the associated review when
      // saving the draft
      await dispatch(changeSelectedCommunity(null));
    }

    const response = await _saveDraft(draft, config.service.drafts, {
      depositState: getState().deposit,
      dispatchFn: dispatch,
      failType: DRAFT_PUBLISH_FAILED,
      partialValidationActionType: DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
    });

    const draftWithLinks = response.data;
    try {
      const response = await config.service.drafts.publish(draftWithLinks.links);
      // after publishing, redirect to the published record
      const recordURL = response.data.links.self_html;
      window.location.replace(recordURL);
    } catch (error) {
      dispatch({
        type: DRAFT_PUBLISH_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

export const submitReview = (draft, { reviewComment, directPublish }) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_SUBMIT_REVIEW_STARTED,
      payload: {
        reviewComment,
      },
      directPublish,
    });

    const response = await _saveDraft(draft, config.service.drafts, {
      depositState: getState().deposit,
      dispatchFn: dispatch,
      failType: DRAFT_SUBMIT_REVIEW_FAILED,
      partialValidationActionType: DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS,
    });

    const draftWithLinks = response.data;
    try {
      const reqResponse = await config.service.drafts.submitReview(
        draftWithLinks.links,
        reviewComment
      );
      const nextURL = reqResponse.data.links.next_html;
      window.location.replace(nextURL);
    } catch (error) {
      dispatch({
        type: DRAFT_SUBMIT_REVIEW_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

export const preview = (draft) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_PREVIEW_STARTED,
    });

    const response = await _saveDraft(draft, config.service.drafts, {
      depositState: getState().deposit,
      dispatchFn: dispatch,
      failType: DRAFT_PREVIEW_FAILED,
      partialValidationActionType: DRAFT_HAS_VALIDATION_ERRORS,
    });
    const recordUrl = response.data.links.record_html;
    // redirect to the preview page
    window.location = `${recordUrl}?preview=1`;
  };
};

/**
 * Returns the function that controls draft deletion.
 *
 * This function is different from the save/publish above because this thunk
 * is independent of form submission.
 */
export const delete_ = () => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DRAFT_DELETE_STARTED,
    });

    try {
      const draft = getState().deposit.record;
      await config.service.drafts.delete(draft.links);

      // redirect to the the uploads page after deleting/discarding a draft
      const redirectURL = "/me/uploads";
      window.location.replace(redirectURL);
    } catch (error) {
      dispatch({
        type: DRAFT_DELETE_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

/**
 * Reserve the PID after having saved the current draft
 */
export const reservePID = (draft, { pidType }) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: RESERVE_PID_STARTED,
      payload: { pidType: pidType },
    });

    try {
      let response = await saveDraftWithUrlUpdate(draft, config.service.drafts);

      const draftWithLinks = response.data;
      response = await config.service.drafts.reservePID(draftWithLinks.links, pidType);

      dispatch({
        type: RESERVE_PID_SUCCEEDED,
        payload: { data: response.data },
      });
    } catch (error) {
      dispatch({
        type: RESERVE_PID_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

/**
 * Discard a previously reserved PID
 */
export const discardPID = (draft, { pidType }) => {
  return async (dispatch, getState, config) => {
    dispatch({
      type: DISCARD_PID_STARTED,
      payload: { pidType: pidType },
    });

    try {
      let response = await saveDraftWithUrlUpdate(draft, config.service.drafts);

      const draftWithLinks = response.data;
      response = await config.service.drafts.discardPID(draftWithLinks.links, pidType);

      dispatch({
        type: DISCARD_PID_SUCCEEDED,
        payload: { data: response.data },
      });
    } catch (error) {
      dispatch({
        type: DISCARD_PID_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

export const changeSelectedCommunity = (community) => {
  return async (dispatch) => {
    dispatch({
      type: SET_COMMUNITY,
      payload: { community },
    });
  };
};
